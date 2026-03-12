class Gmux < Formula
  desc "Composable Claude Code agent team harness"
  homepage "https://github.com/gperalto/gmux"
  url "https://github.com/gioperalto/gmux/archive/refs/tags/v0.2.1.tar.gz"
  sha256 "451bb9bb5730c4173e58bcc9a6e9c6923f3ece39a8d1f86f009ce827ad098431"
  license "MIT"

  def install
    bin.install "bin/gmux"
    (share/"gmux/templates").install Dir["templates/*"]
  end
end
