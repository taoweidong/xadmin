import { http } from "@/utils/http";
import type { Result } from "@/api/types";

export const searchDeptListApi = (data?: object) => {
  return http.request<Result>("get", "/api/system/search/depts", {
    params: data
  });
};
export const searchUserListApi = (data?: object) => {
  return http.request<Result>("get", "/api/system/search/users", {
    params: data
  });
};
export const searchRoleListApi = (data?: object) => {
  return http.request<Result>("get", "/api/system/search/roles", {
    params: data
  });
};
export const searchMenuListApi = (data?: object) => {
  return http.request<Result>("get", "/api/system/search/menus", {
    params: data
  });
};
