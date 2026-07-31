module Economoist.Tests.Blocked.FileLevelDiagnostic
import Std.Test (assert_close)
def blocked_file_level_diagnostic() -> unit ! { Test } = {
  bad = (1.0 >= 0.0)
  assert_close(bad, cast(0.0, f32), cast(0.01, f32), "bool is not f32")
}
