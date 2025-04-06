import { textValidationMessages, createAxios } from "../../utils";
import { FieldError, useForm } from "react-hook-form";
import { useState } from "react";
import { useNavigate, NavLink } from "react-router-dom";
import { userPromise } from "../../redux/slices/userSlice";
import { useDispatch } from "react-redux";
import { Dispatch } from "@reduxjs/toolkit";
import { passwordRegex } from "../../utils/regex";
import { toast } from "react-toastify";

function Login() {
    const {
        register,
        handleSubmit,
        formState: { errors }
    } = useForm<{ identifier: string; password: string }>();
    const [error, setError] = useState<Error | null>(null);

    if (error) {
        return <div>Error: {error.message}</div>;
    }

    const dispatch: Dispatch<any> = useDispatch();

    const navigate = useNavigate();

    const formSubmit = async (data: {
        identifier: string;
        password: string;
    }) => {
        try {
            const mainAxios = createAxios("main");
            const res = await mainAxios.post("/login", data);
            const { user, token } = res.data;
            localStorage.setItem("token", token);
            const actionObj = userPromise(token);
            dispatch(actionObj);
            toast.success("Login successful!");
            navigate(`/user/home`);
        } catch (err) {
            console.error("Login error:", err);
            toast.error((err as Error).message || "Invalid credentials");
            setError(err as Error);
        }
    };

    return (
        <>
            <div className="flex justify-center items-center min-h-screen bg-gray-100">
                <div className="content-section w-full max-w-lg mx-auto pt-3 pb-3 px-4 rounded-lg shadow-lg bg-white">
                    <div className="flex justify-center mb-4">
                        <img
                            src="src/assets/Logo.png"
                            alt="Sevaksha Logo"
                            className="h-20"
                        />
                    </div>
                    <h1 className="text-3xl font-bold text-center text-indigo-900">
                        LOGIN{" "}
                    </h1>
                    <hr className="border-t-1 border-black-400 mt-4 mb-6" />

                    <form
                        noValidate
                        className="mx-auto"
                        onSubmit={handleSubmit(formSubmit)}
                    >
                        <div className="mb-6">
                            <label
                                htmlFor="identifier"
                                className="block text-indigo-900 text-lg font-medium mb-2"
                            >
                                Email / Phone
                            </label>
                            <input
                                type="text"
                                className="input w-full text-lg p-3 border-2 rounded-md border-gray-300 focus:border-orange-400 focus:outline-none"
                                maxLength={50}
                                placeholder="Enter your email or phone number"
                                {...register("identifier", {
                                    required:
                                        "Email or phone number is required",
                                    minLength: {
                                        value: 5,
                                        message:
                                            "Please enter a valid email or phone number"
                                    },
                                    maxLength: {
                                        value: 50,
                                        message: "Input exceeds maximum length"
                                    }
                                })}
                            />
                            {errors.identifier && (
                                <p className="text-red-500 mt-2 text-sm">
                                    {(errors.identifier as FieldError).message}
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
                            <span className="text-gray-600">
                                Don't have an account?{" "}
                            </span>
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
