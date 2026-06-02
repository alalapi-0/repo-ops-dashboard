# Cursor Task Prompt — {{task_id}}

你是 Cursor，请根据以下 task_spec 在指定工作目录推进任务。

## 任务

- **task_id**: {{task_id}}
- **project_id**: {{project_id}}
- **标题**: {{title}}
- **状态**: {{status}} · **优先级**: {{priority}}
- **类型**: {{task_type}}
- **工作目录**: {{working_directory}}

## 描述

{{description}}

## 范围

{{scope}}

## 禁止

{{out_of_scope}}

## 参考路径

{{reference_paths}}

## 验收标准

{{acceptance_criteria}}

## 预期产物

{{artifacts_expected}}

## 验证命令

{{validation_commands}}

## 卡点

{{blockers}}

## 策略

- **playbook**: {{playbook_id}}
- **确认策略**: {{confirmation_policy}}
- **execpolicy**: {{execpolicy_profile}}

## 边界

- 不读取 `.env`、密钥、token、私钥
- 不修改被管理业务仓库（除非 HumanOwner 在目标仓内明确授权）
- 默认 dry-run；外部 API 禁止

---
生成时间：{{generated_at}}
