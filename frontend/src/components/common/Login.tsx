import { textValidationMessages, createAxios } from "../../utils";
import { FieldError, useForm } from "react-hook-form";
import { useState } from "react";
import { usernameRegex, passwordRegex } from "../../utils/regex";
import { useNavigate, NavLink } from "react-router-dom";
import { userPromise } from "../../redux/slices/userSlice";
import { useDispatch } from "react-redux";
import { Dispatch } from "@reduxjs/toolkit";

interface Props {}

function Login({}: Props) {
    const {
        register,
        handleSubmit,
        formState: { errors }
    } = useForm();
    const [error, setError] = useState<Error | null>(null);

    if (error) {
        return <div>Error: {error.message}</div>;
    }

    const dispatch: Dispatch<any> = useDispatch();

    const navigate = useNavigate();

    const formSubmit = async (data: Partial<User>) => {
        try {
            const mainAxios = createAxios("");
            // const res = await mainAxios.post("/login", data);
            // const { user, token } = res.data;
            // localStorage.setItem("token", token);
            // const actionObj = userPromise(token);
            // dispatch(actionObj);
            navigate(`/user/home`);
        } catch (err) {
            console.log(err);
        }
    };

    return (
        <>
            <div className="flex justify-center items-center min-h-screen bg-gray-100">
                <div className="content-section w-full max-w-lg mx-auto pt-3 pb-3 px-4 rounded-lg shadow-lg bg-white">
                    <div className="flex justify-center mb-4">
                        <img src="src/assets/Logo.png" alt="Sevaksha Logo" className="h-20" />
                    </div>
                    <h1 className="text-3xl font-bold text-center text-indigo-900">LOGIN </h1>
                    {/* <p className="text-center text-gray-600 mt-2">Unified Government Welfare Scheme Portal</p> */}
                    <hr className="border-t-1 border-black-400 mt-4 mb-6" />
                    
                    <form
                        noValidate
                        className="mx-auto"
                        onSubmit={handleSubmit(formSubmit)}
                    >
                        <div className="mb-6">
                            <label
                                htmlFor="username"
                                className="block text-indigo-900 text-lg font-medium mb-2"
                            >
                                Username
                            </label>
                            <input
                                type="text"
                                className="input w-full text-lg p-3 border-2 rounded-md border-gray-300 focus:border-orange-400 focus:outline-none"
                                maxLength={32}
                                placeholder="Enter your username"
                                {...register(
                                    "username",
                                    textValidationMessages(
                                        "Username",
                                        5,
                                        32,
                                        usernameRegex
                                    )
                                )}
                            />
                            {errors.username && (
                                <p className="text-red-500 mt-2 text-sm">
                                    {(errors.username as FieldError).message}
                                </p>
                            )}
                        </div>
                        <div className="mb-4">
                            <label
                                htmlFor="password"
                                className="block text-indigo-900 text-lg font-medium mb-2"
                            >
                                Password
                            </label>
                            <input
                                type="password"
                                className="input w-full text-lg p-3 border-2 rounded-md border-gray-300 focus:border-orange-400 focus:outline-none"
                                maxLength={60}
                                placeholder="Enter your password"
                                {...register(
                                    "password",
                                    textValidationMessages(
                                        "Password",
                                        8,
                                        60,
                                        passwordRegex
                                    )
                                )}
                            />
                            {errors.password && (
                                <p className="text-red-500 mt-2 text-sm">
                                    {(errors.password as FieldError).message}
                                </p>
                            )}
                        </div>
                        <div className="flex justify-end mb-6">
                            <NavLink
                                className="text-orange-500 hover:text-orange-600 text-sm font-medium"
                                to="/reset-password"
                            >
                                Forgot Password?
                            </NavLink>
                        </div>
                        <div className="flex justify-center">
                            <button
                                className="btn w-full py-3 bg-indigo-900 hover:bg-indigo-800 text-white text-lg font-medium rounded-md transition-colors"
                                type="submit"
                            >
                                Login
                            </button>
                        </div>
                        <div className="mt-6 text-center">
                            <span className="text-gray-600">Don't have an account? </span>
                            <NavLink
                                className="text-orange-500 hover:text-orange-600 font-medium"
                                to="/register"
                            >
                                Register Now
                            </NavLink>
                        </div>
                    </form>
                </div>
            </div>
        </>
    );
}

export default Login;