import axios from 'axios';

export const api = axios.create({
  baseURL: 'https://bankx.local',      // <-- central place
  withCredentials: false
});

