import axios from "axios";

const client = axios.create({
  baseURL: "http://127.0.0.1:8000",
  "Access-Control-Allow-Origin": "*",
  headers: {
    post: { "Content-Type": "application/json" },
    put: { "Content-Type": "application/json" },
  },
});

const getAuthToken = () => localStorage.getItem("token");

const authInterceptor = (config) => {
  const token = getAuthToken();

  config.headers["Authorization"] = token ? `Token ${token}` : "";

  return config;
};

const errorInterceptor = (error) => {
  switch (error.response.status) {
    case 400:
      console.log(error.response.data);
      break;
    case 401:
      // TODO router push login
      console.log(error.response.data);
      break;
    case 403:
      // TODO not aloud
      console.log(error.response.data);
      break;
    case 404:
      // TODO router push 404
      console.log(error.response.data);
      break;
    case 409:
      // TODO thing you created exists
      console.log(error.response.data);
      break;
    default:
      break;
  }
  return Promise.reject(error);
};

const responseInterceptor = (response) => {
  return response;
};

client.interceptors.request.use(authInterceptor);
client.interceptors.response.use(responseInterceptor, errorInterceptor);

export default client;
