class Gmux < Formula
  desc "Composable Claude Code agent team harness"
  homepage "https://github.com/gperalto/gmux"
  url "https://github.com/gperalto/gmux/archive/refs/tags/v0.2.0.tar.gz"
  license "MIT"

  def install
    bin.install "bin/gmux"
    (share/"gmux/templates").install Dir["templates/*"]
  end
end
