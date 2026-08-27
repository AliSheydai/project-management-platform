import { describe, expect, it } from "vitest";
import { AxiosError } from "axios";
import { getApiErrorMessage, getApiErrorCode } from "@/lib/api/error";

describe("getApiErrorMessage", () => {
  it("reads backend error envelope", () => {
    const error = new AxiosError("fail");
    error.response = {
      status: 400,
      data: { error: { code: "VALIDATION_ERROR", message: "ایمیل تکراری است", details: null } },
      statusText: "Bad Request",
      headers: {},
      config: {} as never,
    };
    expect(getApiErrorMessage(error)).toBe("ایمیل تکراری است");
    expect(getApiErrorCode(error)).toBe("VALIDATION_ERROR");
  });

  it("maps 401 status", () => {
    const error = new AxiosError("unauthorized");
    error.response = {
      status: 401,
      data: {},
      statusText: "Unauthorized",
      headers: {},
      config: {} as never,
    };
    expect(getApiErrorMessage(error)).toContain("منقضی");
  });

  it("handles unknown errors", () => {
    expect(getApiErrorMessage(new Error("x"))).toBe("خطای غیرمنتظره‌ای رخ داد.");
  });
});
