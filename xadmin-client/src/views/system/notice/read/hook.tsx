import {
  getCurrentInstance,
  h,
  reactive,
  ref,
  type Ref,
  shallowRef
} from "vue";
import { noticeReadApi } from "@/api/system/notice";
import { deviceDetection } from "@pureadmin/utils";
import { addDialog } from "@/components/ReDialog";
import { useRouter } from "vue-router";
import { getDefaultAuths, hasAuth } from "@/router/utils";
import { useI18n } from "vue-i18n";
import type { PageTableColumn, OperationProps } from "@/components/RePlusPage";
import { renderSwitch, usePublicHooks } from "@/components/RePlusPage";
import NoticeShowForm from "@/views/system/components/NoticeShow.vue";

export function useNoticeRead(tableRef: Ref) {
  const { t } = useI18n();

  const api = reactive(noticeReadApi);

  const auth = reactive({
    state: false,
    ...getDefaultAuths(getCurrentInstance(), ["state"])
  });
  const switchLoadMap = ref({});
  const { switchStyle } = usePublicHooks();

  const operationButtonsProps = shallowRef<OperationProps>({
    width: 140,
    buttons: [
      {
        code: "detail",
        onClick({ row: { notice_info } }) {
          addDialog({
            title: t("noticeRead.showSystemNotice"),
            props: {
              formInline: { ...notice_info },
              hasPublish: false
            },
            width: "70%",
            draggable: true,
            fullscreen: deviceDetection(),
            fullscreenIcon: true,
            closeOnClickModal: false,
            hideFooter: true,
            contentRenderer: () => h(NoticeShowForm)
          });
        },
        update: true
      }
    ]
  });
  const listColumnsFormat = (columns: PageTableColumn[]) => {
    columns.forEach(column => {
      switch (column._column?.key) {
        case "notice_info":
          column["cellRenderer"] = ({ row }) => (
            <el-link
              type={row.notice_info?.level?.value}
              onClick={() => onGoNoticeDetail(row as any)}
            >
              {row.notice_info.title}
            </el-link>
          );
          break;
        case "owner":
          column["cellRenderer"] = ({ row }) => (
            <el-link onClick={() => onGoUserDetail(row as any)}>
              {row.owner?.username ? row.owner?.username : "/"}
            </el-link>
          );
          break;
        case "unread":
          column["cellRenderer"] = renderSwitch({
            t,
            updateApi: api.state,
            switchLoadMap,
            switchStyle,
            field: column.prop,
            disabled: () => !auth.state,
            success() {
              tableRef.value.handleGetData();
            },
            actionMap: {
              true: t("labels.read"),
              false: t("labels.unread")
            },
            activeMap: {
              false: true,
              true: false
            }
          });
          break;
      }
    });
    return columns;
  };
  const router = useRouter();

  function onGoUserDetail(row: any) {
    if (hasAuth("list:SystemUser") && row.owner && row.owner?.pk) {
      router.push({
        name: "SystemUser",
        query: { pk: row.owner.pk }
      });
    }
  }

  function onGoNoticeDetail(row: any) {
    if (
      hasAuth("list:SystemNotice") &&
      row?.notice_info &&
      row.notice_info?.pk
    ) {
      router.push({
        name: "SystemNotice",
        query: { pk: row.notice_info.pk }
      });
    }
  }

  return {
    api,
    auth,
    listColumnsFormat,
    operationButtonsProps
  };
}
