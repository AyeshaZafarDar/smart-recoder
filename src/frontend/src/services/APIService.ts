class APIService {
  private static instance: APIService;
  private baseUrl: string;
  private appVersion: string;

  private constructor() {
    this.baseUrl = "http://localhost:3002";
    this.appVersion = "1.2.0"; // updated version
  }

  public static getInstance(): APIService {
    if (!APIService.instance) {
      APIService.instance = new APIService();
    }
    return APIService.instance;
  }

  public setAppVersion(version: string): void {
    this.appVersion = version;
  }

  public async request(
    endpoint: string,
    method: string,
    body?: any,
    token?: string,
    auth: boolean = false
  ): Promise<any> {
    const headers: HeadersInit = {
      "app-version": this.appVersion,
    };

    if (auth && token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    if (!(body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method,
        headers,
        body: body ? (body instanceof FormData ? body : JSON.stringify(body)) : null,
      });

      if (response?.status === 426) {
        return {
          updateRequired: true,
          message: "Please update your client application.",
        };
      }

      if (!response.ok) {
        console.log("Unexpected error occurred");
        return null;
      }

      return response.json();
    } catch (error) {
      console.log("Unexpected error occurred");
      return null;
    }
  }

  public async uploadFile(endpoint: string, file: Blob, token?: string): Promise<any> {
    const formData = new FormData();
    formData.append("file", file);

    return this.request(endpoint, "POST", formData, token, true);
  }
}

export default APIService.getInstance();
