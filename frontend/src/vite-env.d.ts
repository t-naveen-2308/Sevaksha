/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_API_BASE_URL: string;
    readonly VITE_TIMEOUT: number;
    readonly VITE_IMAGE_MAX_SIZE: number;
    readonly VITE_PDF_MAX_SIZE: number;
    readonly VITE_NODE_ENV: string;
}

interface ImportMeta
{
    readonly env: ImportMetaEnv;
}

declare global {
    interface User {
        id: string;
        name: string;
        username: string;
        email: string;
        password: string;
        profilePicture: string;
    }

    interface Scheme {
        scheme_id: number;
        scheme_name: string;
        min_age?: number | null;
        max_age?: number | null;
        income_limit?: number | null;
        target_occupation?: string | null;
        eligibility_criteria?: string | null;
        required_documents?: string | null;
        scheme_description?: string | null;
        application_process?: string | null;
        benefits?: string | null;
        application_link?: string | null;
        language_support?: string | null;
        is_active: boolean;
        created_at: string;
        updated_at: string;
    }

    interface RootState {
        user: UserState;
    }
}

export {};