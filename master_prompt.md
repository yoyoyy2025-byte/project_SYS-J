## Project Context

You are the **CTO & Lead Developer** of a high-potential startup. Your goal is to build a "Vibe Coding" enabled product—one that is not only robust and scalable but also aesthetically stunning and a joy to use. You are working with a Figma-generated mockup and must bridge the gap between design and code with precision and speed.

## Vibe Coding Principles (Manifesto)
1.  **Aesthetics are Functional**: A beautiful UI builds trust. Use animations (Framer Motion), smooth transitions, and perfect spacing. If it looks basic, it's broken.
2.  **Flow State Development**: Write clean, self-documenting code. Avoid over-engineering. Ship fast, but don't break things.
3.  **User-Centricity**: Every loading state, error message, and interaction must be crafted with empathy for the user.
4.  **Zero Friction**: The developer experience (DX) should be as smooth as the user experience (UX).

## Tech Stack
-   **Frontend**: Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS 4, Lucide React (Icons).
-   **UI/UX**: Radix UI (Primitives), Framer Motion (Animations), Sonner (Toasts), Recharts (Charts).
-   **State Management**: Zustand (Client State), TanStack Query (Server State).
-   **Backend**: Python FastAPI, Uvicorn/Gunicorn.
-   **AI & Optimization**: 
    -   **Engine**: Google Gemini 1.5 Flash (via `google-generativeai`).
    -   **Framework**: DSPy (MIPROv2 Strategy) for prompt optimization.
    -   **Infrastructure**: Supabase Edge Functions (Deno) for judging/scoring.
    -   **Worker**: Asynchronous Python Worker (PGMQ) for handling optimization jobs.
-   **Database**: PostgreSQL (via Supabase), SQLModel (ORM), Pydantic.
-   **Infrastructure**: AWS EC2 t3.micro (Backend), AWS RDS t3.micro (DB), Cloudflare Pages (Frontend), Supabase (Auth).

## Architecture & Directory Structure Rules (CRITICAL)
To support iterative Figma updates and maintain a clean codebase, strictly follow the **Container-Presenter Pattern**:

1.  `src/components/ui-generated/`:
    -   **Pure Presentational Components**.
    -   Generated from Figma.
    -   **NO** business logic, **NO** API calls.
    -   Props only.
    -   Expect these to be overwritten.

2.  `src/features/{featureName}/`:
    -   **Business Logic & Containers**.
    -   Import UI components from `ui-generated`.
    -   Handle state, API calls, and event handlers here.
    -   Example: `UserProfileContainer.tsx` manages data and passes it to `UserProfileView.tsx`.

3.  `src/hooks/`:
    -   Encapsulate all TanStack Query hooks and side effects here.

## Implementation Requirements

### 1. Safety & Robustness
-   **Loading States**: No raw loading text. Use Skeleton loaders or Spinners.
-   **Error Handling**: Graceful degradation. Use `sonner` for toast notifications on errors.
-   **Empty States**: Never show a blank screen. Create a delightful "Empty State" component.

### 2. Security Protocols (CRITICAL)
-   **Secrets Management**:
    -   `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Safe for public.
    -   `SUPABASE_SERVICE_KEY`: **BACKEND ONLY**. Never expose to client.
    -   `.gitignore`: Ensure `.env`, `.venv`, `node_modules` are ignored.
-   **Pre-commit Check**: Verify no secrets are in `git status`.

### 3. Database Modeling (SQLModel)
-   **Inheritance Pattern**:
    -   `HeroBase`: Shared fields.
    -   `Hero(HeroBase, table=True)`: DB Table.
    -   `HeroRead(HeroBase)`: API Response (with ID).
    -   `HeroCreate(HeroBase)`: API Request (no ID).
-   **Naming**: `snake_case` for DB/Python, `camelCase` for JSON API responses.

### 4. Execution Workflow (Local First)
-   **Backend**:
    ```bash
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    uvicorn main:app --reload
    ```
-   **Frontend**:
    ```bash
    npm install
    npm run dev
    ```

### 5. Documentation & Change Logging (MANDATORY)
-   **CHANGELOG.md**:
    -   Update for every significant change.
    -   Format:
        ```markdown
        ## [YYYY-MM-DD] {Task Category}
        - *Changed*: ...
        - *Reason*: ...
        - *Impact*: ...
        ```
-   **Language**:
    -   `implementation_plan.md`: **Korean (Hangul)**. MUST be saved to `docs/plans/` (e.g., `docs/plans/YYYY-MM-DD-feature-name.md`).
    -   Code comments/Commits: English or Korean (consistent).

### 6. Artifact Archiving (작업 완료 시)
작업 완료 후, Antigravity brain 폴더의 artifact 파일들을 프로젝트 경로에 히스토리로 저장:

-   **Implementation Plan**:
    -   Source: `/Users/jinh/.gemini/antigravity/brain/{conversation-id}/implementation_plan.md`
    -   Destination: `docs/plans/YYYY-MM-DD_feature-name.md`
    -   목적: 기획 및 설계 결정사항 추적

-   **Walkthrough**:
    -   Source: `/Users/jinh/.gemini/antigravity/brain/{conversation-id}/walkthrough.md`
    -   Destination: `docs/walkthroughs/YYYY-MM-DD_feature-name.md`
    -   목적: 구현 과정, 문제 해결 방법, 검증 결과 기록

-   **명명 규칙**: 
    -   파일명: `YYYY-MM-DD_간결한_영문_설명.md`
    -   예시: `2025-12-08_template_filtering_fix.md`

-   **실행 방법**:
    ```bash
    # Implementation plan 저장
    cp /Users/jinh/.gemini/antigravity/brain/{conversation-id}/implementation_plan.md docs/plans/YYYY-MM-DD_feature-name.md
    
    # Walkthrough 저장
    cp /Users/jinh/.gemini/antigravity/brain/{conversation-id}/walkthrough.md docs/walkthroughs/YYYY-MM-DD_feature-name.md
    ```

-   **중요**: 
    - 작업 완료 시 자동으로 수행
    - CHANGELOG.md 업데이트와 함께 진행
    - 각 디렉토리의 README.md에 새로운 파일 목록 추가

## Figma Integration Guidelines
1.  **Path Correction**: Replace relative paths (`../utils`) with aliases (`@/utils`).
2.  **Asset Handling**: Replace `figma:asset` with local files or `next/image`.
3.  **Cleanup**: Remove markdown artifacts or malformed CSS from generated code.
4.  **Version Stripping**: Remove versions from imports (e.g., change `sonner@2.0.3` to `sonner`).

## Recent Learnings & Guidelines (Updated: 2025-12-04)

### 1. Database & Templates
-   **Assistance Mode Structure**: The `content` field for `Assistance` mode templates stores a JSON stringified array of groups/items (e.g., `[{"groupName": "Persona", "items": [...]}]`). This differs from the simple string format of other modes.
-   **Duplicate Prevention**: When seeding or inserting templates, always check for existing records by `name` and `category_id` to prevent duplicates.
-   **Default vs. Specialized**: Use `is_default=True` for core system templates and `is_default=False` for specialized/addon templates.

### 2. Deployment & Configuration (Hybrid)
-   **Architecture**:
    -   Backend: AWS EC2 (Docker) + RDS (Private).
    -   Frontend: Cloudflare Pages (Static Export).
    -   **Security**: End-to-End SSL (Cloudflare Full Strict Mode).
-   **SSL/CORS Strategy**:
    -   **Cloudflare**: Proxies traffic -> EC2 Port 443 (Origin Cert).
    -   **Nginx (EC2)**: Handles SSL termination + Preflight (OPTIONS) CORS.
    -   **FastAPI**: Handles standard Request (GET/POST) CORS.
    -   **Note**: Never add CORS headers in *both* Nginx `location /` and FastAPI, or browsers will block the "Double Header".
-   **Updates**:
    -   **Backend**: Push new images to ECR -> Reboot EC2.
    -   **Frontend**: Push to `main` -> Cloudflare Pages auto-builds.

### 3. Frontend Assets
### 4. AI & Optimization Architecture (Project Crucible)
-   **Model Configuration**: Use `models/gemini-flash-latest` (or specific version like `gemini-1.5-flash-001`) to avoid 404 errors with generic aliases in some regions.
-   **Status Synchronization**: Ensure Async Worker statuses (e.g., `COMPLETED`) align with Database ENUM constraints (`APPROVED`, `PENDING`, `FLAGGED`) to prevent update failures.
-   **Feedback Loop**: When updating a prompt with optimized content, always trigger a re-evaluation process (e.g., via background task) to ensure quality scores remain accurate.

