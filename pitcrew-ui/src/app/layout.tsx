import type { Metadata } from "next";
import { CopilotKit } from "@copilotkit/react-core";
import "@copilotkit/react-ui/styles.css";
import "./globals.css";

// NOTE: the scaffold used next/font/google, which fetches from Google at BUILD
// time. That turns a wifi blip at the venue into a failed build. System font
// stacks cost nothing visually here and cannot fail offline.
export const metadata: Metadata = {
  title: "Pit Crew",
  description: "Every PR gets a pit stop.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col">
        {/* Points at /api/copilotkit, which runs on Fireworks rather than OpenAI. */}
        <CopilotKit runtimeUrl="/api/copilotkit">{children}</CopilotKit>
      </body>
    </html>
  );
}
