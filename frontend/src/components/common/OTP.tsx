import { useForm } from "react-hook-form";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createAxios } from "../../utils";

function OTP() {
    const {
        register,
        handleSubmit,
        formState: { errors }
    } = useForm<{ otp: string }>();
    const [error, setError] = useState<string | null>(null);
    const [resendDisabled, setResendDisabled] = useState(false);
    const [countdown, setCountdown] = useState(30);

    const navigate = useNavigate();

    const formSubmit = async (data: { otp: string }) => {
        try {
            const mainAxios = createAxios("main");
            const res = await mainAxios.post("/verify-otp", {
                otp: data.otp
            });
            navigate("/user/home");
        } catch (err) {
            setError("Invalid OTP. Please try again.");
        }
    };

    const handleResendOTP = async () => {
        try {
            setResendDisabled(true);
            const mainAxios = createAxios("main");
            // Replace with your actual resend OTP API endpoint
            await mainAxios.post("/resend-otp");

            // Start countdown
            let timeLeft = 30;
            const timer = setInterval(() => {
                if (timeLeft <= 0) {
                    clearInterval(timer);
                    setResendDisabled(false);
                    setCountdown(30);
                } else {
                    setCountdown(timeLeft);
                    timeLeft -= 1;
                }
            }, 1000);
        } catch (err) {
            setError("Failed to resend OTP. Please try again.");
            setResendDisabled(false);
        }
    };

    return (
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
                    OTP Verification
                </h1>
                <p className="text-center text-gray-600 mt-2">
                    Please enter the OTP sent to your email/phone
                </p>
                <hr className="border-t-1 border-black-400 mt-4 mb-6" />

                {error && (
                    <div className="mb-4 text-red-500 text-center">{error}</div>
                )}

                <form
                    noValidate
                    className="mx-auto"
                    onSubmit={handleSubmit(formSubmit)}
                >
                    <div className="mb-6">
                        <input
                            type="text"
                            className="input w-full text-lg p-3 border-2 rounded-md border-gray-300 focus:border-orange-400 focus:outline-none text-center tracking-widest"
                            maxLength={6}
                            placeholder="Enter OTP"
                            {...register("otp", {
                                required: "OTP is required",
                                pattern: {
                                    value: /^[0-9]{6}$/,
                                    message: "Please enter a valid 6-digit OTP"
                                }
                            })}
                        />
                        {errors.otp && (
                            <p className="text-red-500 mt-2 text-sm text-center">
                                {errors.otp.message}
                            </p>
                        )}
                    </div>

                    <div className="flex justify-center">
                        <button
                            className="btn w-full py-3 bg-indigo-900 hover:bg-indigo-800 text-white text-lg font-medium rounded-md transition-colors"
                            type="submit"
                        >
                            Verify OTP
                        </button>
                    </div>

                    <div className="mt-6 text-center">
                        <button
                            type="button"
                            onClick={handleResendOTP}
                            disabled={resendDisabled}
                            className={`text-orange-500 hover:text-orange-600 font-medium ${
                                resendDisabled
                                    ? "opacity-50 cursor-not-allowed"
                                    : ""
                            }`}
                        >
                            {resendDisabled
                                ? `Resend OTP in ${countdown}s`
                                : "Resend OTP"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default OTP;
