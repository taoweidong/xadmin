import { BaseApi, ViewBaseApi } from "@/api/base";
import type { DetailResult } from "@/api/types";
//系统设置
export const settingsApi = new BaseApi("/api/settings/setting");

// 基本配置
export const settingsBasicApi = new ViewBaseApi("/api/settings/basic");

// 密码设置
export const settingsPasswordApi = new ViewBaseApi("/api/settings/password");

// 登录配置
export const settingsLoginLimitApi = new ViewBaseApi(
  "/api/settings/login/limit"
);
export const settingsLoginAuthApi = new ViewBaseApi("/api/settings/login/auth");

// 邮箱配置
export const settingsEmailApi = new ViewBaseApi("/api/settings/email");
// 注册配置
export const settingsRegisterAuthApi = new ViewBaseApi(
  "/api/settings/register/auth"
);

// 短信
class SettingsSmsServerApi extends ViewBaseApi {
  backends = (params?: object) => {
    return this.request<DetailResult>(
      "get",
      params,
      {},
      `${this.baseApi}/backends`
    );
  };
}
export const settingsSmsServerApi = new SettingsSmsServerApi(
  "/api/settings/sms"
);

export const settingsSmsConfigApi = new ViewBaseApi("/api/settings/sms/config");

// 验证码设置
export const settingsVerifyCodeApi = new ViewBaseApi("/api/settings/verify");

// 忘记密码设置
export const settingsResetPasswordCodeApi = new ViewBaseApi(
  "/api/settings/reset/auth"
);

// 图片验证码设置
export const settingsCaptchaApi = new ViewBaseApi("/api/settings/captcha");

// 绑定邮箱手机设置
export const settingsBindEmailApi = new ViewBaseApi("/api/settings/bind/email");
export const settingsBindPhoneApi = new ViewBaseApi("/api/settings/bind/phone");

// ip黑名单
export const settingsBlockIpApi = new BaseApi("/api/settings/ip/block");
