"""Mốc dịch vụ launchd được phép trong user/<uid kiểm> theo bản macOS (D68, D157).

Chỉ nhãn ĐÃ ĐO trên máy thật; đổi bản macOS thì đo lại ở G3.8. 24G90 (máy B, 18/10/2026 21:06): user/503 sau khi macOS
tự bật dịch vụ Apple cho tram-kiem — 52 nhãn, đều `com.apple.*`, hai lần `print` liên tiếp giống hệt
(`~/.tram/g3/g3b-20261018210646-89993-user-{2,3}.out`). Sáng 18/10 (miền mới) là rỗng — rỗng vẫn hợp lệ.
Rủi ro còn lại (D68): so theo NHÃN — job lạ mượn đúng nhãn đã có sẽ không bị bắt ở lớp này."""
import re

# Nhãn `com.apple.mdworker.shared.<0N000000-0M00-0000-0000-000000000000>` đổi M mỗi lần macOS bật lại (đo 21:06 → 0100,
# 21:17 → 0200): khớp theo MẪU hẹp này thay vì từng nhãn (D157).
MAU_USER = re.compile(r"com\.apple\.mdworker\.shared\.0[1-9]000000-0[0-9]00-0000-0000-000000000000")

# Khối `endpoints` của user/<uid kiểm> không còn rỗng khi có dịch vụ Apple (đo 21:06/21:17: 73 dòng, đều com.apple.*):
# chấp nhận khi MỌI dòng là endpoint Mach của `com.apple.*` (D157); job lạ vẫn lộ ở khối `services` theo mốc.
DONG_ENDPOINT = re.compile(r"\t\t *(0|0x[0-9a-f]+) +M +[AD] +com\.apple\.[A-Za-z0-9._@-]+")

MOC_USER: dict[str, frozenset[str]] = {"24G90": frozenset({
    "com.apple.ContainerMigrationService",
    "com.apple.CoreAuthentication.agent",
    "com.apple.DictionaryServiceHelper",
    "com.apple.SetStoreUpdateService",
    "com.apple.SpeechRecognitionCore.brokerd",
    "com.apple.TrustEvaluationAgent",
    "com.apple.TrustedPeersHelper",
    "com.apple.accessibility.mediaaccessibilityd",
    "com.apple.carboncore.csnameddata",
    "com.apple.cfprefsd.xpc.agent",
    "com.apple.contactsd",
    "com.apple.containermanagerd",
    "com.apple.coreimportd",
    "com.apple.ctkd",
    "com.apple.cvmsCompAgent3425AMD_x86_64",
    "com.apple.cvmsCompAgent3425AMD_x86_64_1",
    "com.apple.cvmsCompAgent3600_arm64",
    "com.apple.cvmsCompAgent3600_arm64_1",
    "com.apple.cvmsCompAgent3600_x86_64",
    "com.apple.cvmsCompAgent3600_x86_64_1",
    "com.apple.cvmsCompAgent_x86_64",
    "com.apple.cvmsCompAgent_x86_64_1",
    "com.apple.distnoted.xpc.agent",
    "com.apple.fskit.fskit_agent",
    "com.apple.geod",
    "com.apple.hiservices-xpcservice",
    "com.apple.installandsetup.migrationhelper.user",
    "com.apple.iokit.IOServiceAuthorizeAgent",
    "com.apple.keychainsharingmessagingd",
    "com.apple.lsd",
    "com.apple.mbbackgrounduseragent",
    "com.apple.mdworker.mail",
    "com.apple.mdworker.shared",
    "com.apple.mdworker.single.arm64",
    "com.apple.mdworker.single.x86_64",
    "com.apple.mdworker.sizing",
    "com.apple.metadata.mdbulkimport",
    "com.apple.metadata.mdflagwriter",
    "com.apple.netauth.user.auth",
    "com.apple.pluginkit.pkd",
    "com.apple.secd",
    "com.apple.secinitd",
    "com.apple.security.KeychainStasher",
    "com.apple.security.XPCKeychainSandboxCheck",
    "com.apple.security.XPCTimeStampingService",
    "com.apple.speech.speechsynthesisd.arm64",
    "com.apple.speech.speechsynthesisd.x86_64",
    "com.apple.trustd.agent",
    "com.apple.usermanagerhelper",
})}
