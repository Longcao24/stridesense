#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate an English build of the phone demo: read index.html, translate every
user-facing Chinese string -> write index_en.html.  Code comments are left as-is
(not user-visible).  Any translation key that matches 0 times is printed so it can
be fixed (guards against typos in the Chinese source text)."""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()

R = []
def add(z, e): R.append((z, e))

# ---------- document head / shell ----------
add('lang="zh-CN"', 'lang="en"')
add('手机轨迹复现器 · Phone Motion Tracker', 'Phone Motion Tracker')
add('📱 手机轨迹复现器', '📱 Phone Motion Tracker')
add('用陀螺仪 + 加速度计实时复现「旋转姿态」与「空中画圈轨迹」 · 单文件 · 无依赖',
    'Real-time reconstruction of orientation &amp; in-air path from gyroscope + accelerometer · single file · zero dependencies')

# ---------- permission card ----------
add('⚠️ 当前不是安全上下文(HTTPS / localhost)。iOS 不会弹出传感器授权,请用 README 里的 HTTPS 方式打开。',
    '⚠️ Not a secure context (HTTPS / localhost). iOS will not prompt for sensor access — open this page over HTTPS as described in the README.')
add('① 授权并启动传感器', '① Grant &amp; start sensors')

# ---------- mode / control buttons ----------
add('✍️ 手势模式', '✍️ Gesture mode')
add('🚶 步行模式 PDR', '🚶 Walk mode (PDR)')
add('② 校准(静置)', '② Calibrate (hold still)')
add('③ 开始录制', '③ Start recording')
add('▶ 回放', '▶ Replay')
add('▶ 开始步行追踪', '▶ Start walk tracking')
add('>清空</button>', '>Clear</button>')
add('未校准。请把手机平放静置后点「校准」。', 'Not calibrated. Lay the phone flat and still, then tap "Calibrate".')

# ---------- canvas labels ----------
add('🧭 姿态 / 旋转(可靠)', '🧭 Orientation / rotation (reliable)')
add('✍️ 空间轨迹(短手势)', '✍️ Spatial path (short gesture)')
add('等待传感器数据…', 'Waiting for sensor data…')

# ---------- reconstruction params (gesture) ----------
add('⚙️ 轨迹重建参数(画圈不准就调这里)', '⚙️ Path reconstruction params (tune here if the shape looks off)')
add('停止录制后会对整段数据做<b>边界约束重建</b>(假设手势<b>首尾静止</b>,消掉重力残差与漂移),',
    'On stop, the whole segment is rebuilt with <b>boundary constraints</b> (assuming the gesture <b>starts and ends at rest</b>, cancelling residual gravity &amp; drift), ')
add('这是轨迹能成形的关键。要点:<b>开始前静置一下 → 画(2~4秒)→ 末尾再静置一下</b>再停。',
    'which is what lets the path take shape. Key: <b>hold still → draw (2–4 s) → hold still again</b> before stopping. ')
add('画圈勾「闭合手势」。参数改完会自动重算,不满意点「↻ 重建」即可,不用重画。',
    'For loops, tick "Closed gesture". Params recompute automatically; if unhappy, tap "↻ Rebuild" — no need to redraw.')
add('▸ 重建参数(改完自动重算,不用重画手势)', '▸ Reconstruction params (auto-recompute on change, no redraw needed)')
add('平滑窗口 smooth(降噪)', 'Smoothing window (denoise)')
add('首尾静止去漂(强烈建议)', 'Detrend with still endpoints (recommended)')
add('闭合手势(画圈)', 'Closed gesture (loop)')
add('↻ 用当前参数重建', '↻ Rebuild with current params')
add('▸ 实时预览滤波(只影响录制时的粗预览,不影响最终重建)',
    '▸ Live-preview filter (affects only the rough live preview, not the final rebuild)')
add('速度泄漏 leak', 'Velocity leak')
add('静止判定 ZUPT(m/s²)', 'Still threshold ZUPT (m/s²)')
add('偏置高通 k', 'Bias high-pass k')
add('⬇ 导出 JSON', '⬇ Export JSON')
add('⬇ 导出 CSV', '⬇ Export CSV')
add('⬆ 上传给电脑(让 Claude 分析)', '⬆ Upload to computer (for analysis)')

# ---------- walk card ----------
add('🚶 步行模式 · 足绑 PDR', '🚶 Walk mode · foot-mounted PDR')
add('把手机<b>绑在脚背或脚踝</b>(屏幕朝外、绑紧别晃),平放静置点「② 校准」,再点上面「▶ 开始步行追踪」,正常走路。<br>',
    'Strap the phone <b>to the top of your foot or ankle</b> (screen facing out, snug, no wobble). Hold still and tap "② Calibrate", then tap "▶ Start walk tracking" above and walk normally.<br>')
add('原理:每步<b>落地静止</b>那一刻速度必为 0 → 自动 <b>ZUPT</b> 把这一步累积的漂移清掉,所以能连续走很远不飘。',
    'How it works: the instant each step <b>lands and is still</b>, velocity must be 0 → an automatic <b>ZUPT</b> wipes the drift built up over that step, so you can walk far without drifting.')
add('右图俯视就是你走的<b>地面路线</b>,还会数步数、算距离。',
    'The right (top-down) view is the <b>ground path</b> you walked; it also counts steps and distance.')
add('🧹 清空路径', '🧹 Clear path')
add('▸ 落地(ZUPT)检测参数 — 检不到步/乱跳时调', '▸ Stance (ZUPT) detection params — tune if steps are missed / jumpy')
add('加速度偏差阈值 accTh(m/s²)', 'Accel deviation threshold accTh (m/s²)')
add('陀螺阈值 gyroTh(deg/s)', 'Gyro threshold gyroTh (deg/s)')
add('落地确认窗口 N(采样)', 'Stance-confirm window N (samples)')
add('没检测到步 → 调大 accTh / gyroTh;静止时也乱算步 → 调小。',
    'No steps detected → raise accTh / gyroTh; phantom steps while still → lower them.')

# ---------- gait card ----------
add('📊 步态分析(随走动实时更新)', '📊 Gait analysis (updates live as you walk)')
add('开始步行追踪后,这里显示步频、步速、支撑/摆动相、步态变异性 CV、足倾角等。',
    'After you start walk tracking, this shows cadence, speed, stance/swing phase, gait variability CV, foot pitch, and more.')
add('⬆ 上传步态数据(给 Claude)', '⬆ Upload gait data (for analysis)')

# ---------- help section ----------
add('📖 使用说明 & 原理', '📖 How to use &amp; how it works')
add('<b>旋转/姿态</b>:左图实时跟随手机朝向,几乎不漂移 → 可靠。<br><br>',
    '<b>Rotation / orientation</b>: the left view follows the phone orientation in real time, almost no drift → reliable.<br><br>')
add('<b>空中画圈</b>:右图把手在空中划过的路径画出来。流程:<br>',
    '<b>In-air drawing</b>: the right view traces the path your hand sweeps through the air. Steps:<br>')
add('1. 手机平放静置 → 点「校准重力」(约 1.5 秒,别动)。<br>',
    '1. Lay the phone flat and still → tap "Calibrate gravity" (~1.5 s, do not move).<br>')
add('2. 点「开始录制」。<br>', '2. Tap "Start recording".<br>')
add('3. 拿起手机在空中画一个圈 / 写个字(2~4 秒内)。<br>',
    '3. Pick up the phone and draw a circle / write a character in the air (within 2–4 s).<br>')
add('4. 点「停止录制」,右图显示轨迹;「回放」可动画重演;「导出」存数据给 Python 分析。<br><br>',
    '4. Tap "Stop recording" — the right view shows the path; "Replay" animates it; "Export" saves the data for Python analysis.<br><br>')
add('<b>物理局限(诚实说明)</b>:位置=加速度的二次积分,误差随时间平方累积,超过 ~5–10 秒必漂移。',
    '<b>Physical limits (honest note)</b>: position = double integral of acceleration, so error grows with time squared and inevitably drifts beyond ~5–10 s.')
add('本工具靠「高通去偏置 + 零速更新 ZUPT + 速度泄漏」让短手势<b>形状可辨认</b>,但不是物理精确的厘米级尺度。',
    'This tool uses high-pass bias removal + zero-velocity update (ZUPT) + velocity leak to keep short gestures <b>shape-recognizable</b>, but it is not physically accurate at centimeter scale.')
add('要厘米级请上视觉/磁/RF 辅助(对应你做的 freehand US 思路)。',
    'For centimeter accuracy, add visual / magnetic / RF aiding.')

# ---------- JS: permission / status ----------
add('iOS 需要 HTTPS(或 localhost)才能授权传感器。请用 README 里的 HTTPS 方式打开本页。',
    'iOS needs HTTPS (or localhost) to grant sensor access. Open this page over HTTPS as in the README.')
add('授权请求失败:', 'Permission request failed: ')
add('。请确认是通过 HTTPS 打开。', '. Make sure you opened it over HTTPS.')
add('用户拒绝了传感器授权。请刷新重试。', 'Sensor permission denied. Refresh and try again.')
add('传感器已启动 ✓ 摇一摇 / 转一转看看左图是否响应。',
    'Sensors started ✓ Shake / rotate the phone to see the left view respond.')
add('devicemotion(无)', 'devicemotion (none)')
add('deviceorientation(无)', 'deviceorientation (none)')
add('采样≈', 'rate≈')

# ---------- JS: calibration ----------
add('传感器还没数据,先点①授权并启动。', 'No sensor data yet — tap ① Grant & start first.')
add('请先停止录制再校准。', 'Stop recording before calibrating.')
add('请先停止步行追踪再校准。', 'Stop walk tracking before calibrating.')
add('校准中…请保持手机静止 1.5 秒', 'Calibrating… keep the phone still for 1.5 s')
add('校准样本太少,请重试(确认①已启动)。', 'Too few calibration samples — try again (make sure ① is started).')
add('校准完成 ✓ 重力 |g|=', 'Calibrated ✓ gravity |g|=')
add(' m/s²。现在可「开始录制」并在空中画手势。', ' m/s². Now Start recording and draw a gesture in the air.')

# ---------- JS: recording ----------
add('请先「校准重力」再录制。', 'Calibrate gravity before recording.')
add('■ 停止录制', '■ Stop recording')
add('● 录制中…', '● Recording…')
add(' 静置一下→画圈/写字(2~4秒)→末尾再静置一下', ' hold still → draw/write (2–4 s) → hold still again')
add('录制过短(<b>', 'Recording too short (<b>')
add('</b> 采样),无法重建。请重新「开始录制」画 2~4 秒。',
    '</b> samples) — cannot rebuild. Tap Start recording again and draw for 2–4 s.')
add('录制结束:<b>', 'Recording done: <b>')
add('</b> 采样, ', '</b> samples, ')
add(' 秒, 源:<b>', ' s, source: <b>')
add('</b>。已重建;调下方参数可「↻ 重建」,或「回放/导出」。',
    '</b>. Rebuilt; tune the params below to "↻ Rebuild", or Replay / Export.')
add('已清空。', 'Cleared.')

# ---------- JS: gesture upload ----------
add('还没有可上传的轨迹,先录制一段(2~4 秒)。', 'No path to upload yet — record a segment first (2–4 s).')
add('上传中…', 'Uploading…')
add('已上传到电脑 ✓ <b>uploads/', 'Uploaded to computer ✓ <b>uploads/')
add('</b> —— 现在可以让 Claude 分析了', '</b> —— ready for analysis')
add('上传失败 HTTP ', 'Upload failed HTTP ')
add('(确认服务器是支持上传的新版)', ' (make sure the server supports uploads)')
add('上传失败:', 'Upload failed: ')

# ---------- JS: walk ----------
add('请先「校准」(脚先别动,静置 1.5 秒)再开始步行追踪。',
    'Calibrate first (keep your foot still for 1.5 s) before walk tracking.')
add('■ 停止', '■ Stop')
add('● 步行追踪中…', '● Walk tracking…')
add(' 绑脚上正常走动,每步落地会自动 ZUPT 校正。',
    ' Walk normally with the phone strapped on; each footfall auto-corrects via ZUPT.')
add('步行停止 ✓ 跨步 <b>', 'Walk stopped ✓ strides <b>')
add('</b>(≈', '</b> (≈')
add(' 步),距离 <b>', ' steps), distance <b>')
add('</b> m。下方为步态分析。', '</b> m. Gait analysis below.')
add('路径已清空。', 'Path cleared.')
add('还没有足够的步态数据,先走几步。', 'Not enough gait data yet — take a few steps.')
add('已上传 ✓ <b>uploads/', 'Uploaded ✓ <b>uploads/')
add('</b> — 可让 Claude 分析步态了', '</b> — gait data ready for analysis')

# ---------- JS: gait panel ----------
add('CV采集中', 'CV collecting')
add('⏱ 时间', '⏱ Timing')
add('跨步频 cadence', 'Cadence')
add('</b> 跨步/分 <span ', '</b> strides/min <span ')
add(' 步/分)</span>', ' steps/min)</span>')
add('跨步时/步态周期', 'Stride time / gait cycle')
add('摆动时间 swing', 'Swing time')
add('支撑相占比', 'Stance phase %')
add('📏 空间', '📏 Space')
add('步速 speed', 'Speed')
add('跨步长 stride len', 'Stride length')
add('步长 step length', 'Step length')
add('(≈跨步÷2)', '(≈stride÷2)')
add('抬脚高度*', 'Foot clearance*')
add('信号弱', 'weak signal')
add('(偏大·疑含漂移·需标定)', '(large · likely drift · needs calibration)')
add('(幅度', '(amp ')
add('🦶 运动学', '🦶 Kinematics')
add('着地足倾角 HS', 'Foot pitch @HS')
add('离地足倾角 TO', 'Foot pitch @TO')
add('摆动峰值角速度', 'Peak swing ang. vel.')
add('着地冲击(相对)', 'Landing impact (rel.)')
add('🔄 转身', '🔄 Turning')
add('转身步数 / 累计转向', 'Turn steps / total turn')
add(' 步 / ', ' steps / ')
add('⚠️ 需第二只脚(单脚测不了)', '⚠️ Needs a second foot (cannot measure single-foot)')
add('双支撑时间', 'Double-support time')
add('需对侧脚', 'needs other foot')
add('步宽', 'Step width')
add('需双脚', 'needs both feet')
add('左右对称性', 'L/R symmetry')
add('基于 <b>', 'Based on <b>')
add('</b> 个跨步稳态(去首尾各1步)。CV 需≥', '</b> steady-state strides (first &amp; last dropped). CV shows at ≥')
add('跨步才显示。', ' strides.')
add('注:单脚每个步态周期摆动一次=1 个<b>跨步(stride)</b>,故所有指标按跨步计;日常"步数"≈2×跨步(左右对称假设);临床 CV 阈值正是按跨步,可直接对照。步长=跨步÷2(对称假设)。*抬脚高度:竖直弧线形状(抬起→到顶→落地)是真实的,但绝对量级不确定——可能含摆动旋转期的重力泄漏放大。需用已知高度(如跨过一本书)对照标定出比例系数后才可信;形状/相对趋势可用。',
    'Note: one foot swings once per gait cycle = 1 <b>stride</b>, so every metric is per-stride; everyday "steps" ≈ 2× strides (assuming L/R symmetry); clinical CV thresholds are per-stride and directly comparable. Step length = stride ÷ 2 (symmetry assumption). *Foot clearance: the vertical arc shape (lift → peak → land) is real, but the absolute magnitude is uncertain — it may include gravity-leak amplification during swing rotation. Trust the magnitude only after calibrating a scale factor against a known height (e.g. stepping over a book); shape / relative trend are usable.')

# ---------- JS: mode-switch path titles ----------
add('🗺️ 步行路线(俯视)', '🗺️ Walk path (top view)')

# ---------- JS: canvas placeholders / overlays ----------
add('录制中…画个圈', 'Recording… draw a circle')
add('录制后这里显示轨迹', 'Path appears here after recording')
add('视野≈', 'view≈')
add('m · 平面', 'm · plane ')
add("label:'屏'", "label:'Scr'")
add('点「▶ 开始步行追踪」后走动', 'Tap "▶ Start walk tracking" then walk')
add("'跨步 '", "'strides '")
add('m · 视野', 'm · view ')
add('走动后显示 3D 路线', '3D path appears after walking')
add('录制后显示 3D 轨迹', '3D path appears after recording')
add('3D · 拖动旋转 · 视野', '3D · drag to rotate · view ')

# ---------- JS: live readout (walk) ----------
add('步行 PDR · 源 ', 'Walk PDR · src ')
add("'追踪中'", "'tracking'")
add("'已停止'", "'stopped'")
add('状态  ', 'State  ')
add("'● 落地 (ZUPT)'", "'● stance (ZUPT)'")
add("'○ 摆动中'", "'○ swing'")
add('跨步  ', 'Strides  ')
add(' 步)', ' steps)')
add('距离  ', 'Dist  ')
add(' m   位置 [', ' m   pos [')

# ---------- JS: live readout (gesture) ----------
add('采样 ', 'Rate ')
add('Hz · 加速度源 ', 'Hz · accel src ')
add(' · 录制 ', ' · rec ')
add('姿态  α=', 'Att  α=')
add('速度  v=[', 'Vel  v=[')
add('位置  p=[', 'Pos  p=[')
add('· 静止ZUPT', '· still ZUPT')

# ---------- JS: accel source labels ----------
add('userAccel融合', 'userAccel (fused)')
add('手动减重力', 'manual −gravity')

# ---------- apply (longest key first so nested phrases win) ----------
missing = [z for z, _ in R if z not in src]
out = src
for z, e in sorted(R, key=lambda p: -len(p[0])):
    out = out.replace(z, e)

open(os.path.join(HERE, "index_en.html"), "w", encoding="utf-8").write(out)

print("rules: %d   wrote index_en.html (%d bytes)" % (len(R), len(out)))
if missing:
    print("!! %d keys matched 0 times (fix these):" % len(missing))
    for m in missing:
        print("   -", m[:60])
else:
    print("all keys matched ✓")
