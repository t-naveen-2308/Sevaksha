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
    age: number;
    income: number;
    occupation: string;
    gender: 'Male' | 'Female';
    marital_status: 'Never Married' | 'Currently Married' | 'Widowed' | 'Divorced' | 'Separated';
}

function AddOrEditUser({ to }: Props) {
    const {
        register,
        handleSubmit,
        setValue,
        formState: { errors }
    } = useForm<User>();
    const [error, setError] = useState<Error | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    if (to === "edit") {
        useEffect(() => {
            const fetchUserData = async () => {
                try {
                    setIsLoading(true);
                    const axiosInstance = createAxios("user");
                    const response = await axiosInstance.get("/user/profile");
                    
                    // Pre-fill all form fields with existing user data
                    setValue("name", response.data.name);
                    setValue("username", response.data.username);
                    setValue("email", response.data.email);
                    setValue("age", response.data.age);
                    setValue("income", response.data.income);
                    setValue("occupation", response.data.occupation);
                    setValue("gender", response.data.gender);
                    setValue("marital_status", response.data.marital_status);
                } catch (err) {
                    console.error("Failed to fetch user data:", err);
                    setError(err as Error);
                } finally {
                    setIsLoading(false);
                }
            };

            fetchUserData();
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

    if (isLoading) {
        return (
            <div className="flex justify-center items-center min-h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-900"></div>
            </div>
        );
    }

    const formSubmit = async (data: User) => {
        try {
            setIsLoading(true);
            const mainAxios = createAxios("");
            
            if (to === "add") {
                await mainAxios.post("/register", data);
                navigate("/login");
                flash('Registration successful! Please login.', 'success');
            } else {
                await mainAxios.put("/user/profile", data);
                navigate("/user/profile");
                flash('Profile updated successfully!', 'success');
            }
        } catch (err) {
            console.error("Form submission error:", err);
            setError(err as Error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex justify-center items-center min-h-screen bg-gray-100">
            <div className="content-section w-full max-w-2xl mx-auto pt-6 pb-8 px-8 rounded-lg shadow-lg bg-white">
                <div className="flex justify-center mb-4">
                    <img src="src/assets/Logo.png" alt="Sevaksha Logo" className="h-20" />
                </div>
                <h1 className="text-3xl font-bold text-center text-indigo-900">
                    {to === "add" ? "REGISTER" : "EDIT PROFILE"}
                </h1>
                
                
                <hr className="border-t-1 border-gray-300 mt-4 mb-6" />
                
                <form noValidate onSubmit={handleSubmit(formSubmit)} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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

                        {/* Age Field */}
                        <div>
                            <label
                                htmlFor="age"
                                className="block text-indigo-900 text-lg font-medium mb-2"
                            >
                                Age
                            </label>
                            <input
                                type="number"
                                id="age"
                                className="w-full text-lg p-3 border-2 rounded-md border-gray-300 focus:border-orange-400 focus:outline-none"
                                placeholder="Enter your age"
                                {...register("age", {
                                    required: "Age is required",
                                    min: {
                                        value: 18,
                                        message: "You must be at least 18 years old"
                                    },
                                    max: {
                                        value: 120,
                                        message: "Please enter a valid age"
                                    }
                                })}
                            />
                            {errors.age && (
                                <p className="text-red-500 mt-2 text-sm">
                                    {(errors.age as FieldError).message}
                                </p>
                            )}
                        </div>

                        {/* Income Field */}
                        <div>
                            <label
                                htmlFor="income"
                                className="block text-indigo-900 text-lg font-medium mb-2"
                            >
                                Monthly Income (₹)
                            </label>
                            <div className="relative">
                                <span className="absolute left-3 top-3 text-gray-500">₹</span>
                                <input
                                    type="number"
                                    id="income"
                                    className="w-full text-lg p-3 pl-8 border-2 rounded-md border-gray-300 focus:border-orange-400 focus:outline-none"
                                    placeholder="Enter your monthly income"
                                    {...register("income", {
                                        required: "Income is required",
                                        min: {
                                            value: 0,
                                            message: "Income cannot be negative"
                                        }
                                    })}
                                />
                            </div>
                            {errors.income && (
                                <p className="text-red-500 mt-2 text-sm">
                                    {(errors.income as FieldError).message}
                                </p>
                            )}
                        </div>

                        {/* Occupation Field */}
                        <div>
                            <label
                                htmlFor="occupation"
                                className="block text-indigo-900 text-lg font-medium mb-2"
                            >
                                Occupation
                            </label>
                            <input
                                type="text"
                                id="occupation"
                                className="w-full text-lg p-3 border-2 rounded-md border-gray-300 focus:border-orange-400 focus:outline-none"
                                placeholder="Enter your occupation"
                                {...register("occupation", {
                                    required: "Occupation is required",
                                    maxLength: {
                                        value: 100,
                                        message: "Occupation cannot exceed 100 characters"
                                    }
                                })}
                            />
                            {errors.occupation && (
                                <p className="text-red-500 mt-2 text-sm">
                                    {(errors.occupation as FieldError).message}
                                </p>
                            )}
                        </div>

                        {/* Gender Field */}
                        <div>
                            <label
                                htmlFor="gender"
                                className="block text-indigo-900 text-lg font-medium mb-2"
                            >
                                Gender
                            </label>
                            <select
                                id="gender"
                                className="w-full text-lg p-3 border-2 rounded-md border-gray-300 focus:border-orange-400 focus:outline-none"
                                {...register("gender", {
                                    required: "Gender is required"
                                })}
                            >
                                <option value="">Select Gender</option>
                                <option value="Male">Male</option>
                                <option value="Female">Female</option>
                            </select>
                            {errors.gender && (
                                <p className="text-red-500 mt-2 text-sm">
                                    {(errors.gender as FieldError).message}
                                </p>
                            )}
                        </div>

                        {/* Marital Status Field */}
                        <div>
                            <label
                                htmlFor="marital_status"
                                className="block text-indigo-900 text-lg font-medium mb-2"
                            >
                                Marital Status
                            </label>
                            <select
                                id="marital_status"
                                className="w-full text-lg p-3 border-2 rounded-md border-gray-300 focus:border-orange-400 focus:outline-none"
                                {...register("marital_status", {
                                    required: "Marital status is required"
                                })}
                            >
                                <option value="">Select Marital Status</option>
                                <option value="Never Married">Never Married</option>
                                <option value="Currently Married">Currently Married</option>
                                <option value="Widowed">Widowed</option>
                                <option value="Divorced">Divorced</option>
                                <option value="Separated">Separated</option>
                            </select>
                            {errors.marital_status && (
                                <p className="text-red-500 mt-2 text-sm">
                                    {(errors.marital_status as FieldError).message}
                                </p>
                            )}
                        </div>

                        {/* Password Field */}
                        <div className="md:col-span-2">
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
                                placeholder={to === "add" ? "Create secure password" : "Enter new password (leave blank to keep current)"}
                                {...register(
                                    "password",
                                    to === "add" ? 
                                    textValidationMessages(
                                        "Password",
                                        8,
                                        60,
                                        passwordRegex
                                    ) : {
                                        required: false,
                                        minLength: {
                                            value: 8,
                                            message: "Password must be at least 8 characters"
                                        },
                                        pattern: {
                                            value: passwordRegex,
                                            message: "Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character"
                                        }
                                    }
                                )}
                            />
                            {errors.password && (
                                <p className="text-red-500 mt-2 text-sm">
                                    {(errors.password as FieldError).message}
                                </p>
                            )}
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex justify-between pt-6">
                        <button
                            type="button"
                            onClick={() => navigate(-1)}
                            className="px-6 py-3 bg-gray-300 hover:bg-gray-400 text-gray-800 text-lg font-medium rounded-md transition-colors"
                            disabled={isLoading}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="px-6 py-3 bg-indigo-900 hover:bg-indigo-800 text-white text-lg font-medium rounded-md transition-colors flex items-center justify-center"
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <>
                                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Processing...
                                </>
                            ) : (
                                to === "add" ? "Register" : "Update Profile"
                            )}
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