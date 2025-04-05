import {
    textValidationMessages,
    createAxios
} from "../../utils";
import { FieldError, useForm } from "react-hook-form";
import { useEffect, useState } from "react";
import {
    nameRegex,
    usernameRegex,
    emailRegex,
    passwordRegex
} from "../../utils/regex";
import { NavLink, useNavigate } from "react-router-dom";

interface Props {
    to: "add" | "edit";
}

interface User {
    name: string;
    username: string;
    email: string;
    password: string;
}

function AddOrEditUser({ to }: Props) {
    const {
        register,
        handleSubmit,
        setValue,
        formState: { errors }
    } = useForm<User>();
    const [error, setError] = useState<Error | null>(null);
    const navigate = useNavigate();

    if (to === "edit") {
        useEffect(() => {
            // Pre-fill form with existing user data in edit mode
            // Example:
            // setValue("name", existingUser.name);
            // setValue("username", existingUser.username);
            // setValue("email", existingUser.email);
        }, [setValue]);
    }

    if (error) {
        return (
            <div className="flex justify-center items-center min-h-screen">
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                    Error: {error.message}
                </div>
            </div>
        );
    }

    const formSubmit = async (data: User) => {
        try {
            const mainAxios = createAxios("");
            // const res = await mainAxios.post(to === "add" ? "/register" : "/edit-user", data);
            // Handle success response
            navigate(to === "add" ? "/login" : "/user/profile");
        } catch (err) {
            console.error(err);
            setError(err as Error);
        }
    };

    return (
        <div className="flex justify-center items-center min-h-screen bg-gray-100">
            <div className="content-section w-full max-w-md mx-auto pt-6 pb-8 px-8 rounded-lg shadow-lg bg-white">
                <div className="flex justify-center mb-4">
                    <img src="src/assets/Logo.png" alt="Sevaksha Logo" className="h-20" />
                </div>
                <h1 className="text-3xl font-bold text-center text-indigo-900">
                    {to === "add" ? "REGISTER" : "EDIT PROFILE"}
                </h1>
            
                <hr className="border-t-1 border-gray-300 mt-4 mb-6" />
                
                <form noValidate onSubmit={handleSubmit(formSubmit)} className="space-y-4">
                    {/* Name Field */}
                    <div>
                        <label
                            htmlFor="name"
                            className="block text-indigo-900 text-lg font-medium mb-2"
                        >
                            Full Name
                        </label>
                        <input
                            type="text"
                            id="name"
                            className="w-full text-lg p-3 border-2 rounded-md border-gray-300 focus:border-orange-400 focus:outline-none"
                            maxLength={60}
                            placeholder="Enter your full name"
                            {...register(
                                "name",
                                textValidationMessages(
                                    "Name",
                                    3,
                                    60,
                                    nameRegex
                                )
                            )}
                        />
                        {errors.name && (
                            <p className="text-red-500 mt-2 text-sm">
                                {(errors.name as FieldError).message}
                            </p>
                        )}
                    </div>

                    {/* Username Field */}
                    <div>
                        <label
                            htmlFor="username"
                            className="block text-indigo-900 text-lg font-medium mb-2"
                        >
                            Username
                        </label>
                        <input
                            type="text"
                            id="username"
                            className="w-full text-lg p-3 border-2 rounded-md border-gray-300 focus:border-orange-400 focus:outline-none"
                            maxLength={32}
                            placeholder="Choose a username"
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

                    {/* Email Field */}
                    <div>
                        <label
                            htmlFor="email"
                            className="block text-indigo-900 text-lg font-medium mb-2"
                        >
                            Email
                        </label>
                        <input
                            type="email"
                            id="email"
                            className="w-full text-lg p-3 border-2 rounded-md border-gray-300 focus:border-orange-400 focus:outline-none"
                            placeholder="Enter your email"
                            {...register("email", {
                                required: `Email is required.`,
                                pattern: {
                                    value: emailRegex,
                                    message: `Please enter a valid email address.`
                                }
                            })}
                        />
                        {errors.email && (
                            <p className="text-red-500 mt-2 text-sm">
                                {(errors.email as FieldError).message}
                            </p>
                        )}
                    </div>

                    {/* Password Field */}
                    <div>
                        <label
                            htmlFor="password"
                            className="block text-indigo-900 text-lg font-medium mb-2"
                        >
                            {to === "add" ? "Create Password" : "New Password"}
                        </label>
                        <input
                            type="password"
                            id="password"
                            className="w-full text-lg p-3 border-2 rounded-md border-gray-300 focus:border-orange-400 focus:outline-none"
                            maxLength={60}
                            placeholder={to === "add" ? "Create secure password" : "Enter new password"}
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

                    {/* Action Buttons */}
                    <div className="flex justify-between pt-4">
                        <button
                            type="button"
                            onClick={() => navigate(-1)}
                            className="px-6 py-3 bg-gray-300 hover:bg-gray-400 text-gray-800 text-lg font-medium rounded-md transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="px-6 py-3 bg-indigo-900 hover:bg-indigo-800 text-white text-lg font-medium rounded-md transition-colors"
                        >
                            {to === "add" ? "Register" : "Update Profile"}
                        </button>
                    </div>

                    {to === "add" && (
                        <div className="pt-4 text-center">
                            <span className="text-gray-600">Already have an account? </span>
                            <NavLink
                                className="text-orange-500 hover:text-orange-600 font-medium"
                                to="/login"
                            >
                                Login Now
                            </NavLink>
                        </div>
                    )}
                </form>
            </div>
        </div>
    );
}

export default AddOrEditUser;