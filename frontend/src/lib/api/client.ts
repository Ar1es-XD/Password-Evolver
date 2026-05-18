import { z } from "zod";

import { env } from "@/lib/config/env";

type ApiOptions<T> = {
    method?: "GET" | "POST" | "DELETE";
    body?: T;
    schema?: z.ZodSchema;
};

export async function apiFetch<TBody, TResponse>(
    path: string,
    options: ApiOptions<TBody> = {}
): Promise<TResponse> {
    const response = await fetch(`${env.apiBaseUrl}${path}`, {
        method: options.method ?? "GET",
        headers: {
            "Content-Type": "application/json"
        },
        body: options.body ? JSON.stringify(options.body) : undefined,
        cache: "no-store"
    });

    if (!response.ok) {
        const message = await response.text();
        throw new Error(message || "Request failed");
    }

    if (options.schema) {
        const json = await response.json();
        return options.schema.parse(json) as TResponse;
    }

    return (await response.json()) as TResponse;
}
