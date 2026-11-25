# HTTP 和函数 Mock 示例

下面的例子使用 Go 标准库，可保存为 `example_test.go`，用 `go test example_test.go` 运行。第一个测试通过真实路由进入 handler，用函数替身控制查询结果。第二个测试通过客户端发出真实的本地 HTTP 请求，由测试服务器扮演上游。

```go
package example

import (
	"context"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/http/httptest"
	"net/url"
	"strings"
	"sync/atomic"
	"testing"
)

type labelLookup func(context.Context, string) (string, error)

func labelHandler(lookup labelLookup) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		id := r.URL.Query().Get("id")
		if id == "" {
			http.Error(w, "id is required", http.StatusBadRequest)
			return
		}
		label, err := lookup(r.Context(), id)
		if err != nil {
			http.Error(w, "lookup unavailable", http.StatusBadGateway)
			return
		}
		if _, err := io.WriteString(w, label); err != nil {
			log.Print("write label response: ", err)
		}
	}
}

func TestLabelAPI(t *testing.T) {
	cases := []struct {
		name       string
		id         string
		lookupErr  error
		wantStatus int
		wantBody   string
		wantCalls  int
	}{
		{name: "success", id: "demo", wantStatus: http.StatusOK, wantBody: "Sample", wantCalls: 1},
		{name: "missing ID", wantStatus: http.StatusBadRequest, wantBody: "id is required"},
		{
			name: "lookup failed", id: "demo", lookupErr: errors.New("unavailable"),
			wantStatus: http.StatusBadGateway, wantBody: "lookup unavailable", wantCalls: 1,
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			calls := 0
			lookup := func(_ context.Context, id string) (string, error) {
				calls++
				if id != tc.id {
					t.Errorf("lookup ID = %q, want %q", id, tc.id)
				}
				return "Sample", tc.lookupErr
			}
			mux := http.NewServeMux()
			mux.Handle("/label", labelHandler(lookup))
			target := "/label?id=" + url.QueryEscape(tc.id)
			recorder := httptest.NewRecorder()
			mux.ServeHTTP(recorder, httptest.NewRequest(http.MethodGet, target, nil))

			response := recorder.Result()
			defer response.Body.Close()
			if response.StatusCode != tc.wantStatus {
				t.Errorf("status = %d, want %d", response.StatusCode, tc.wantStatus)
			}
			if got := strings.TrimSpace(recorder.Body.String()); got != tc.wantBody {
				t.Errorf("body = %q, want %q", got, tc.wantBody)
			}
			if calls != tc.wantCalls {
				t.Errorf("lookup calls = %d, want %d", calls, tc.wantCalls)
			}
		})
	}
}

func fetchLabel(ctx context.Context, client *http.Client, baseURL, id string) (string, error) {
	request, err := http.NewRequestWithContext(ctx, http.MethodGet, baseURL+"/label?id="+url.QueryEscape(id), nil)
	if err != nil {
		return "", err
	}
	response, err := client.Do(request)
	if err != nil {
		return "", err
	}
	defer response.Body.Close()

	if response.StatusCode != http.StatusOK {
		return "", fmt.Errorf("status %d", response.StatusCode)
	}
	body, err := io.ReadAll(response.Body)
	return string(body), err
}

func TestFetchLabel(t *testing.T) {
	var requests atomic.Int32
	upstream := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		requests.Add(1)
		if r.Method != http.MethodGet || r.URL.Path != "/label" || r.URL.Query().Get("id") != "demo" {
			http.Error(w, "unexpected request", http.StatusBadRequest)
			return
		}
		if _, err := io.WriteString(w, "Sample"); err != nil {
			t.Errorf("write upstream response: %v", err)
		}
	}))
	t.Cleanup(upstream.Close)

	got, err := fetchLabel(context.Background(), upstream.Client(), upstream.URL, "demo")
	if err != nil || got != "Sample" {
		t.Fatalf("fetchLabel() = (%q, %v), want (%q, nil)", got, err, "Sample")
	}
	if got := requests.Load(); got != 1 {
		t.Errorf("upstream requests = %d, want 1", got)
	}
}
```

移植时使用目标仓库的路由和 HTTP 客户端。若测试的是 JSON 契约，可解析实际响应体并断言相关字段。只有依赖的调用次数、顺序或参数属于被测约定时，才把它们写进断言。

[Go httptest 文档](https://pkg.go.dev/net/http/httptest)
