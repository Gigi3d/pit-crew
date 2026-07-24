// Destination: pitcrew-ui/app/api/copilotkit/route.ts
//
// The CopilotKit runtime, pointed at FIREWORKS instead of OpenAI. Fireworks is
// OpenAI-compatible, so we hand OpenAIAdapter a client with the Fireworks baseURL.
// This is what deepens your Fireworks usage: the copilot itself runs on it.
//
// Needs: npm install openai
// Confirm CopilotRuntime / OpenAIAdapter exports against your installed
// @copilotkit/runtime version. If your version uses BuiltInAgent instead, the
// quickstart shows that shape; the idea is identical, just point it at Fireworks.
import {
  CopilotRuntime,
  OpenAIAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import OpenAI from "openai";
import { NextRequest } from "next/server";

const openai = new OpenAI({
  apiKey: process.env.FIREWORKS_API_KEY,
  baseURL: "https://api.fireworks.ai/inference/v1",
});

const serviceAdapter = new OpenAIAdapter({
  openai,
  model: "accounts/fireworks/models/deepseek-v3p1",
});

const runtime = new CopilotRuntime();

export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });
  return handleRequest(req);
};
