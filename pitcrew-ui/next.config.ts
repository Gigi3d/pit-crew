import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  // A stray ~/package-lock.json makes Next guess the home dir as the workspace
  // root. Pin it to this app so the build is deterministic wherever it runs.
  turbopack: {
    root: path.join(__dirname),
  },
};

export default nextConfig;
