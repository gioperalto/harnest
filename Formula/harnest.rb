class Harnest < Formula
  desc "Composable Claude Code agent team harness"
  homepage "https://github.com/gioperalto/harnest"
  url "https://github.com/gioperalto/harnest/archive/refs/tags/v1.1.0.tar.gz"
  sha256 ""
  license "MIT"

  def install
    bin.install "bin/harnest"
    (share/"harnest/nest").install Dir["nest/*"]
    (share/"harnest/lib").install Dir["lib/*"]
  end
end
