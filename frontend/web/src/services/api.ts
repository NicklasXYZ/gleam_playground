import * as axios from 'axios';
import { AxiosInstance  } from 'axios';
import * as monaco from "monaco-editor";
import config from './config';

const serverUrl = `${config.serverUrl}`;
const apiShare = `${config.apiShare}`;
const apiRun = `${config.apiRun}`;
const apiKey = `${config.apiKey}`;

const axiosClient = axios.default.create(
    {
        baseURL: serverUrl,
        headers: {
            common: {
              "x-api-key": apiKey,
            }
          }
    }
);

export enum EvalEventKind {
    Stdout = 'stdout',
    Stderr = 'stderr'
}

export interface ShareResponse {
    snippetID: string
}

export interface Snippet {
    fileName: string
    code: string
}

export interface EvalEvent {
    Message: string
    Kind: EvalEventKind
    Delay: number
}

export interface RunResponse {
    formatted?: string | null
    events: EvalEvent[]
}

export interface VersionResponse {
    version: string
}

export interface IAPIClient {
    readonly axiosClient: AxiosInstance

    getVersion(): Promise<VersionResponse>

    getSuggestions(query: { packageName?: string, value?: string }): Promise<monaco.languages.CompletionList>

    evaluateCode(code: string, format: boolean): Promise<RunResponse>

    formatCode(code: string): Promise<RunResponse>

    getSnippet(id: string): Promise<Snippet>

    shareSnippet(code: string): Promise<ShareResponse>
}

export const instantiateStreaming = async (resp, importObject) => {
    if ('instantiateStreaming' in WebAssembly) {
        return await WebAssembly.instantiateStreaming(resp, importObject);
    }

    const source = await (await resp).arrayBuffer();
    return await WebAssembly.instantiate(source, importObject);
};

class Client implements IAPIClient {
    get axiosClient() {
        return this.client;
    }

    constructor(private client: axios.AxiosInstance) {
    }

    async getVersion(): Promise<VersionResponse> {
        return this.get<VersionResponse>(`${apiShare}/version?=${Date.now()}`)
    }

    async getSuggestions(query: { packageName?: string, value?: string }): Promise<monaco.languages.CompletionList> {
        const queryParams = Object.keys(query).map(k => `${k}=${query[k]}`).join('&');
        return this.get<monaco.languages.CompletionList>(`/suggest?${queryParams}`);
    }

    async evaluateCode(code: string, format: boolean): Promise<RunResponse> {
        const req = {code: code}
        return this.post<RunResponse>(`${apiRun}/run?format=${Boolean(format)}`, req);
    }

    async formatCode(code: string): Promise<RunResponse> {
        const req = {code: code}
        return this.post<RunResponse>(`${apiRun}/format`, req);
    }

    async getSnippet(id: string): Promise<Snippet> {
        return this.get<Snippet>(`${apiShare}/snippet/${id}`);
    }

    async shareSnippet(code: string): Promise<ShareResponse> {
        const req = {code: code}
        return this.post<ShareResponse>(`${apiShare}/snippet`, req);
    }

    private async get<T>(uri: string): Promise<T> {
        try {
            const resp = await this.client.get<T>(uri);
            return resp.data;
        } catch (err) {
            throw Client.extractAPIError(err);
        }
    }

    private async post<T>(uri: string, data: any, cfg?: axios.AxiosRequestConfig): Promise<T> {
        try {
            const resp = await this.client.post<T>(uri, data, cfg);
            return resp.data;
        } catch (err) {
            throw Client.extractAPIError(err);
        }
    }

    private static extractAPIError(err: any): Error {
        return new Error(err?.response?.data?.error ?? err.message);
    }
}

export default new Client(axiosClient);
