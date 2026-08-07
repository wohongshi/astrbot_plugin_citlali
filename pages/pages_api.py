"""
WebUI 后端 API
"""
import time

from ..core.time_schedule import (
    get_current_window, get_window_name, CITLALI_SCHEDULE,
    get_schedule_for_webui, save_schedule_from_webui,
)

PLUGIN_NAME = "astrbot_plugin_citlali"


def _ok(data=None):
    return {"status": "ok", "data": data}


def _err(msg):
    return {"status": "error", "message": str(msg)}


def register_pages(plugin):
    reg = plugin.ctx.register_web_api
    P = f"/{PLUGIN_NAME}"

    reg(f"{P}/overview", _overview(plugin), ["GET"], "总览")
    reg(f"{P}/users", _users(plugin), ["GET"], "用户列表")
    reg(f"{P}/user/detail", _user_detail(plugin), ["GET"], "用户详情")
    reg(f"{P}/user/adjust", _user_adjust(plugin), ["POST"], "调整好感度")
    reg(f"{P}/user/reset", _user_reset(plugin), ["POST"], "重置用户")
    reg(f"{P}/user/note", _user_note(plugin), ["POST"], "添加备注")
    reg(f"{P}/graph/overview", _graph(plugin), ["GET"], "图谱")
    reg(f"{P}/schedule/get", _schedule_get(plugin), ["GET"], "获取日程")
    reg(f"{P}/schedule/save", _schedule_save(plugin), ["POST"], "保存日程")
    reg(f"{P}/settings/get", _settings_get(plugin), ["GET"], "获取设置")
    reg(f"{P}/settings/save", _settings_save(plugin), ["POST"], "保存设置")
    reg(f"{P}/settings/reset", _settings_reset(plugin), ["POST"], "重置设置")


def _overview(plugin):
    async def handler():
        stats = plugin.affinity_mgr.get_stats()
        window = get_current_window()
        schedule = CITLALI_SCHEDULE.get(window, {})
        return _ok({
            "stats": stats,
            "schedule": {
                "window": window,
                "window_name": get_window_name(window),
                "activity": schedule.get("activity", ""),
                "mood": schedule.get("mood", ""),
            },
            "config": plugin.settings.get_all(),
        })
    return handler


def _users(plugin):
    async def handler():
        return _ok({"users": plugin.affinity_mgr.get_leaderboard(200)})
    return handler


def _user_detail(plugin):
    async def handler():
        from quart import request
        uid = request.args.get("user_id", "")
        if not uid:
            return _err("missing user_id")
        from ..core.affinity_manager import AffinityStage, STAGE_NAMES, STAGE_THRESHOLDS
        user = plugin.affinity_mgr.get_user(uid)
        stage = AffinityStage(user.get("stage", 0))
        user["stage_name"] = STAGE_NAMES[stage]
        user["current_threshold"] = STAGE_THRESHOLDS[stage]
        stages = sorted(AffinityStage)
        idx = stages.index(stage)
        user["next_threshold"] = STAGE_THRESHOLDS[stages[idx + 1]] if idx < len(stages) - 1 else None
        return _ok(user)
    return handler


def _user_adjust(plugin):
    async def handler():
        from quart import request
        body = await request.get_json(silent=True) or {}
        uid = body.get("user_id", "")
        amount = body.get("amount", 0)
        if not uid:
            return _err("missing user_id")
        delta, upgraded = plugin.affinity_mgr.add_affinity(uid, "manual", amount=amount)
        return _ok({"delta": delta, "upgraded": upgraded})
    return handler


def _user_reset(plugin):
    async def handler():
        from quart import request
        body = await request.get_json(silent=True) or {}
        uid = body.get("user_id", "")
        if uid:
            plugin.affinity_mgr.reset_user(uid)
        return _ok(True)
    return handler


def _user_note(plugin):
    async def handler():
        from quart import request
        body = await request.get_json(silent=True) or {}
        uid = body.get("user_id", "")
        note = body.get("note", "")
        if uid and note:
            plugin.affinity_mgr.add_note(uid, note)
        return _ok(True)
    return handler


def _graph(plugin):
    async def handler():
        return _ok({"nodes": [], "edges": []})
    return handler


def _schedule_get(plugin):
    async def handler():
        return _ok({"schedule": get_schedule_for_webui()})
    return handler


def _schedule_save(plugin):
    async def handler():
        from quart import request
        body = await request.get_json(silent=True) or {}
        save_schedule_from_webui(body)
        return _ok(True)
    return handler


def _settings_get(plugin):
    async def handler():
        return _ok({"settings": plugin.settings.get_all()})
    return handler


def _settings_save(plugin):
    async def handler():
        from quart import request
        body = await request.get_json(silent=True) or {}
        plugin.settings.update(body)
        from ..core.affinity_manager import set_stage_thresholds
        thresholds = plugin.settings.get("stage_thresholds", [0, 50, 150, 400, 800, 1500])
        set_stage_thresholds(thresholds)
        return _ok(True)
    return handler


def _settings_reset(plugin):
    async def handler():
        plugin.settings.reset()
        return _ok(True)
    return handler
