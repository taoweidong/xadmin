import { $t } from "@/plugins/i18n";

const Layout = () => import("@/layout/index.vue");

export default [
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/login/index.vue"),
    meta: {
      title: $t("menus.login"),
      showLink: false,
      rank: 10101
    }
  },
  {
    path: "/redirect",
    component: Layout,
    meta: {
      title: $t("status.hsLoad"),
      showLink: false,
      rank: 10102
    },
    children: [
      {
        path: "/redirect/:path(.*)",
        name: "Redirect",
        component: () => import("@/layout/redirect.vue")
      }
    ]
  },
  // 下面是一个无layout菜单的例子（一个全屏空白页面），因为这种情况极少发生，所以只需要在前端配置即可（配置路径：src/router/modules/remaining.ts）
  {
    path: "/empty",
    name: "Empty",
    component: () => import("@/views/empty/index.vue"),
    meta: {
      title: $t("menus.empty"),
      showLink: false,
      rank: 10103
    }
  },
  {
    path: "/account-settings",
    name: "AccountSettings",
    component: () => import("@/views/account/index.vue"),
    meta: {
      title: $t("menus.accountSettings"),
      showLink: false,
      rank: 104
    }
  }
] satisfies Array<RouteConfigsTable>;
