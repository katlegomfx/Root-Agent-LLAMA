interface ModelConfig {
    name: string;
    temperature: number;
    type: "text" | "vision";
    maxTokens?: number;
}

const MODEL_CONFIGS: { [key: string]: ModelConfig } = {
    "llama3.2-vision": {
        name: "llama3.2-vision",
        temperature: 0.1,
        type: "vision"
    },
    "llama3.2": {
        name: "llama3.2",
        temperature: 0.1,
        type: "text"
    }
};

// Default temperature if model not found in configs
const DEFAULT_TEMPERATURE = 0.1;
const DEFAULT_MAX_TOKENS = 8192;

// Export only text-based models for MODEL_OPTIONS
export const MODEL_OPTIONS = Object.entries(MODEL_CONFIGS)
    .filter(([_, config]) => config.type === "text")
    .map(([key, _]) => key);

export function getModelTemperature(modelName: string): number {
    return MODEL_CONFIGS[modelName]?.temperature ?? DEFAULT_TEMPERATURE;
}

export function getModelMaxTokens(modelName: string): number {
    return MODEL_CONFIGS[modelName]?.maxTokens ?? DEFAULT_MAX_TOKENS;
}

export function getModelConfig(modelName: string): ModelConfig {
    return MODEL_CONFIGS[modelName] ?? {
        name: modelName,
        temperature: DEFAULT_TEMPERATURE,
        type: "text"
    };
}

export function getFallbackModel(): string {
    // Use same model for fallback
    return "llama3.2";
}

export const PRIMARY_MODEL = "llama3.2";
export const VANILLA_MODEL = "llama3.2";

export const PRIMARY_VISION_MODEL = "llama3.2-vision";
export const FALLBACK_VISION_MODEL = "llama3.2-vision";
