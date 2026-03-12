class Gmux < Formula
  desc "Composable Claude Code agent team harness"
  homepage "https://github.com/gperalto/gmux"
  url "https://github.com/gioperalto/gmux/archive/refs/tags/v1.0.0.tar.gz"
  sha256 ""
  license "MIT"

  def install
    bin.install "bin/gmux"
    (share/"gmux/templates").install Dir["templates/*"]
    (share/"gmux/lib").install Dir["lib/*"]
  end
end
