import { defineFakeRoute } from "vite-plugin-fake-server/client";

// 模拟刷新token接口
export default defineFakeRoute([
  {
    url: "/version.json",
    method: "get",
    response: () => {
      return {
        success: true,
        data: { version: "1.2.2", external: "" }
      };
    }
  }
]);
