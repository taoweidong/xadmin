import { ViewBaseApi } from "@/api/base";
import type { BaseResult, ChoicesResult } from "@/api/types";
import { http } from "@/utils/http";

class UserInfoApi extends ViewBaseApi {
  upload = (data?: object) => {
    return http.upload<BaseResult, any>(`${this.baseApi}/upload`, {}, data);
  };
  choices = () => {
    return this.request<ChoicesResult>(
      "get",
      {},
      {},
      `${this.baseApi}/choices`
    );
  };
  reset = (data?: object) => {
    return this.request<BaseResult>(
      "post",
      {},
      data,
      `${this.baseApi}/reset-password`
    );
  };

  bind = (data?: object) => {
    return this.request<BaseResult>("post", {}, data, `${this.baseApi}/bind`);
  };
}

export const userInfoApi = new UserInfoApi("/api/system/userinfo");
