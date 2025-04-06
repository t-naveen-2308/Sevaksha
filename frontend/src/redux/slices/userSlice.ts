import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { createAxios } from "../../utils";

export const userPromise = createAsyncThunk<Partial<User>, string>(
    "user-data",
    async (token, thunkApi) => {
        try {
            const mainAxios = createAxios("main", token);
            const res = await mainAxios.get("/");
            const user: Partial<User> = res.data;
            console.log(user);
            return user;
        } catch (err) {
            return thunkApi.rejectWithValue(err);
        }
    }
);

interface UserState {
    user: Partial<User> | null;
    isPending: boolean;
    errMessage: string;
}

const initialState: UserState = {
    user: null,
    isPending: false,
    errMessage: ""
};

export const userSlice = createSlice({
    name: "userLogin",
    initialState,
    reducers: {
        loginSuccess(state, action) {
            state.user = action.payload;
        },
        logout(state, action) {
            state.user = null;
            state.isPending = false;
            state.errMessage = "";
            console.log(action);
        }
    },
    extraReducers: (builder) => {
        builder
            .addCase(userPromise.pending, (state, action) => {
                state.isPending = true;
                state.errMessage = "";
            console.log(action);
            })
            .addCase(userPromise.fulfilled, (state, action) => {
                state.user = action.payload;
                state.isPending = false;
            })
            .addCase(userPromise.rejected, (state, action) => {
                state.errMessage = action.payload as string;
                state.isPending = false;
            });
    }
});

export const { loginSuccess, logout } = userSlice.actions;
export default userSlice.reducer;
