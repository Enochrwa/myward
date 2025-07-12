import type { Config } from "tailwindcss";

export default {
	darkMode: ["class"],
	content: [
		"./pages/**/*.{ts,tsx}",
		"./components/**/*.{ts,tsx}",
		"./app/**/*.{ts,tsx}",
		"./src/**/*.{ts,tsx}",
	],
	prefix: "",
	theme: {
		container: {
			center: true,
			padding: {
				DEFAULT: '0.5rem',
				xs: '0.75rem',
				sm: '1rem',
				md: '1.5rem',
				lg: '2rem',
				xl: '2.5rem',
				'2xl': '3rem'
			},
			screens: {
				xs: '375px',
				sm: '640px',
				md: '768px',
				lg: '1024px',
				xl: '1280px',
				'2xl': '1400px'
			}
		},
		screens: {
			'xs': '375px',
			'sm': '640px',
			'md': '768px',
			'lg': '1024px',
			'xl': '1280px',
			'2xl': '1536px',
			'3xl': '1920px',
			'4xl': '2560px',
			// Custom breakpoints for extreme responsiveness
			'mobile-xs': {'max': '374px'},
			'mobile-sm': {'min': '375px', 'max': '639px'},
			'tablet': {'min': '640px', 'max': '1023px'},
			'desktop': {'min': '1024px', 'max': '1535px'},
			'desktop-lg': {'min': '1536px'},
			// Height-based breakpoints
			'short': {'raw': '(max-height: 640px)'},
			'tall': {'raw': '(min-height: 900px)'},
		},
		extend: {
			colors: {
				border: 'hsl(var(--border))',
				input: 'hsl(var(--input))',
				ring: 'hsl(var(--ring))',
				background: 'hsl(var(--background))',
				foreground: 'hsl(var(--foreground))',
				primary: {
					DEFAULT: 'hsl(var(--primary))',
					foreground: 'hsl(var(--primary-foreground))'
				},
				secondary: {
					DEFAULT: 'hsl(var(--secondary))',
					foreground: 'hsl(var(--secondary-foreground))'
				},
				destructive: {
					DEFAULT: 'hsl(var(--destructive))',
					foreground: 'hsl(var(--destructive-foreground))'
				},
				muted: {
					DEFAULT: 'hsl(var(--muted))',
					foreground: 'hsl(var(--muted-foreground))'
				},
				accent: {
					DEFAULT: 'hsl(var(--accent))',
					foreground: 'hsl(var(--accent-foreground))'
				},
				popover: {
					DEFAULT: 'hsl(var(--popover))',
					foreground: 'hsl(var(--popover-foreground))'
				},
				card: {
					DEFAULT: 'hsl(var(--card))',
					foreground: 'hsl(var(--card-foreground))'
				},
				sidebar: {
					DEFAULT: 'hsl(var(--sidebar-background))',
					foreground: 'hsl(var(--sidebar-foreground))',
					primary: 'hsl(var(--sidebar-primary))',
					'primary-foreground': 'hsl(var(--sidebar-primary-foreground))',
					accent: 'hsl(var(--sidebar-accent))',
					'accent-foreground': 'hsl(var(--sidebar-accent-foreground))',
					border: 'hsl(var(--sidebar-border))',
					ring: 'hsl(var(--sidebar-ring))'
				},
				// Enhanced OWIS Brand Colors with purple and teal
				owis: {
					forest: '#1a4a3a',
					'forest-light': '#2a5a4a',
					'forest-dark': '#0a3a2a',
					purple: '#9333ea', // Replaced gold with purple
					'purple-light': '#a855f7', // Lighter purple
					'purple-dark': '#7c3aed', // Darker purple
					'off-white': '#F9FAFB', // New off-white, replacing cream and pearl
					cream: '#F9FAFB', // Was #faf7f2, changed to owis.off-white
					'cream-warm': '#fcf9f4', // Keeping as is, seems distinct enough from gray
					'cream-cool': '#f8f5f0', // Keeping as is, seems distinct enough from gray
					emerald: '#50C878', // Replaced sage with emerald
					'emerald-light': '#5FD38F', // Lighter emerald
					'emerald-dark': '#40B060', // Darker emerald
					'deep-blue': '#1A202C', // New deep blue, replacing charcoal
					charcoal: '#1A202C', // Was #2d3748, changed to owis.deep-blue
					'charcoal-light': '#2C3A4F', // Adjusted light version of deep-blue
					'charcoal-dark': '#101620', // Adjusted dark version of deep-blue
					pearl: '#F9FAFB', // Was #f7fafc, changed to owis.off-white
					bronze: '#7c3aed', // Was #6C757D, changed to owis.purple-dark
					'bronze-light': '#a855f7', // Adjusted light version of purple-dark
					'bronze-dark': '#6b21a8', // Adjusted dark version of purple-dark (darker purple)
					mint: '#e6fffa',
					'mint-light': '#f0fffb',
					'mint-dark': '#dcfff9',
					// Dynamic accent colors
					'rose-gold': '#9333ea', // Was #6C757D, changed to owis.purple
					'deep-emerald': '#0f5132',
					'warm-ivory': '#fffef7', // This is a yellow-ish white, might need to be changed depending on strictness
					'midnight-blue': '#191970',
					'sunset-orange': '#ff6b35', // Orange can sometimes be close to yellow/gold
					teal: '#008080',
					'teal-light': '#20B2AA',
					'teal-dark': '#006666',
					sage: '#50C878', // Was #87a96b, changed to owis.emerald
					'sage-light': '#5FD38F', // Was #9bb57b, changed to owis.emerald-light
					'sage-dark': '#40B060'  // Was #75955b, changed to owis.emerald-dark
				}
			},
			borderRadius: {
				lg: 'var(--radius)',
				md: 'calc(var(--radius) - 2px)',
				sm: 'calc(var(--radius) - 4px)',
				'xl': '1rem',
				'2xl': '1.5rem',
				'3xl': '2rem'
			},
			spacing: {
				'18': '4.5rem',
				'88': '22rem',
				'128': '32rem',
				// Ultra responsive spacing
				'xs': '0.125rem',
				'2xs': '0.25rem',
				'3xs': '0.1875rem'
			},
			fontSize: {
				'2xs': ['0.625rem', { lineHeight: '0.75rem' }],
				'xs': ['0.75rem', { lineHeight: '1rem' }],
				'sm': ['0.875rem', { lineHeight: '1.25rem' }],
				'base': ['1rem', { lineHeight: '1.5rem' }],
				'lg': ['1.125rem', { lineHeight: '1.75rem' }],
				'xl': ['1.25rem', { lineHeight: '1.75rem' }],
				'2xl': ['1.5rem', { lineHeight: '2rem' }],
				'3xl': ['1.875rem', { lineHeight: '2.25rem' }],
				'4xl': ['2.25rem', { lineHeight: '2.5rem' }],
				'5xl': ['3rem', { lineHeight: '1' }],
				'6xl': ['3.75rem', { lineHeight: '1' }],
				'7xl': ['4.5rem', { lineHeight: '1' }],
				'8xl': ['6rem', { lineHeight: '1' }],
				'9xl': ['8rem', { lineHeight: '1' }],
				'10xl': ['10rem', { lineHeight: '1' }]
			},
			maxWidth: {
				'2xs': '16rem',
				'3xs': '12rem',
				'4xs': '8rem',
				'5xs': '6rem'
			},
			keyframes: {
				'accordion-down': {
					from: {
						height: '0'
					},
					to: {
						height: 'var(--radix-accordion-content-height)'
					}
				},
				'accordion-up': {
					from: {
						height: 'var(--radix-accordion-content-height)'
					},
					to: {
						height: '0'
					}
				},
				// Enhanced animations for visual excellence
				'fade-in': {
					'0%': {
						opacity: '0',
						transform: 'translateY(20px) scale(0.95)'
					},
					'100%': {
						opacity: '1',
						transform: 'translateY(0) scale(1)'
					}
				},
				'fade-in-up': {
					'0%': {
						opacity: '0',
						transform: 'translateY(30px)'
					},
					'100%': {
						opacity: '1',
						transform: 'translateY(0)'
					}
				},
				'fade-in-down': {
					'0%': {
						opacity: '0',
						transform: 'translateY(-30px)'
					},
					'100%': {
						opacity: '1',
						transform: 'translateY(0)'
					}
				},
				'scale-in': {
					'0%': {
						opacity: '0',
						transform: 'scale(0.8) rotate(-5deg)'
					},
					'100%': {
						opacity: '1',
						transform: 'scale(1) rotate(0deg)'
					}
				},
				'slide-in-right': {
					'0%': {
						opacity: '0',
						transform: 'translateX(100px)'
					},
					'100%': {
						opacity: '1',
						transform: 'translateX(0)'
					}
				},
				'slide-in-left': {
					'0%': {
						opacity: '0',
						transform: 'translateX(-100px)'
					},
					'100%': {
						opacity: '1',
						transform: 'translateX(0)'
					}
				},
				'float': {
					'0%, 100%': {
						transform: 'translateY(0px) rotate(0deg)'
					},
					'50%': {
						transform: 'translateY(-15px) rotate(2deg)'
					}
				},
				'pulse-glow': {
					'0%, 100%': {
						boxShadow: '0 0 20px rgba(147, 51, 234, 0.3)' // Changed to purple
					},
					'50%': {
						boxShadow: '0 0 40px rgba(147, 51, 234, 0.6)' // Changed to purple
					}
				},
				'shimmer': {
					'0%': {
						transform: 'translateX(-100%)'
					},
					'100%': {
						transform: 'translateX(100%)'
					}
				},
				'gradient-flow': {
					'0%': {
						backgroundPosition: '0% 50%'
					},
					'50%': {
						backgroundPosition: '100% 50%'
					},
					'100%': {
						backgroundPosition: '0% 50%'
					}
				},
				'morph': {
					'0%, 100%': {
						borderRadius: '50% 50% 50% 50%'
					},
					'25%': {
						borderRadius: '30% 70% 70% 30%'
					},
					'50%': {
						borderRadius: '70% 30% 30% 70%'
					},
					'75%': {
						borderRadius: '40% 60% 60% 40%'
					}
				},
				'text-reveal': {
					'0%': {
						opacity: '0',
						transform: 'translateY(100%) skewY(10deg)'
					},
					'100%': {
						opacity: '1',
						transform: 'translateY(0) skewY(0deg)'
					}
				}
			},
			animation: {
				'accordion-down': 'accordion-down 0.2s ease-out',
				'accordion-up': 'accordion-up 0.2s ease-out',
				'fade-in': 'fade-in 0.8s ease-out',
				'fade-in-up': 'fade-in-up 0.6s ease-out',
				'fade-in-down': 'fade-in-down 0.6s ease-out',
				'scale-in': 'scale-in 0.5s ease-out',
				'slide-in-right': 'slide-in-right 0.7s ease-out',
				'slide-in-left': 'slide-in-left 0.7s ease-out',
				'float': 'float 4s ease-in-out infinite',
				'float-delayed': 'float 4s ease-in-out infinite 2s',
				'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
				'shimmer': 'shimmer 2.5s ease-in-out infinite',
				'gradient-flow': 'gradient-flow 3s ease infinite',
				'morph': 'morph 8s ease-in-out infinite',
				'text-reveal': 'text-reveal 0.8s ease-out'
			},
			fontFamily: {
				'sans': ['Inter', 'system-ui', 'sans-serif'],
				'heading': ['Playfair Display', 'serif'],
				'display': ['Playfair Display', 'serif']
			},
			backgroundImage: {
				'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
				'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
				'mesh-gradient': 'linear-gradient(135deg, var(--tw-gradient-stops))'
			},
			backdropBlur: {
				'xs': '2px'
			},
			boxShadow: {
				'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
				'medium': '0 4px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 30px -5px rgba(0, 0, 0, 0.05)',
				'large': '0 10px 40px -15px rgba(0, 0, 0, 0.1), 0 20px 50px -10px rgba(0, 0, 0, 0.05)',
				'glow': '0 0 30px rgba(147, 51, 234, 0.3)', // Changed to purple
				'glow-lg': '0 0 50px rgba(147, 51, 234, 0.4)', // Changed to purple
				'xs': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
				'2xs': '0 1px 1px 0 rgba(0, 0, 0, 0.05)'
			},
			gridTemplateColumns: {
				'auto-fit-xs': 'repeat(auto-fit, minmax(8rem, 1fr))',
				'auto-fit-sm': 'repeat(auto-fit, minmax(12rem, 1fr))',
				'auto-fit-md': 'repeat(auto-fit, minmax(16rem, 1fr))',
				'auto-fit-lg': 'repeat(auto-fit, minmax(20rem, 1fr))',
				'auto-fill-xs': 'repeat(auto-fill, minmax(8rem, 1fr))',
				'auto-fill-sm': 'repeat(auto-fill, minmax(12rem, 1fr))',
				'auto-fill-md': 'repeat(auto-fill, minmax(16rem, 1fr))',
				'auto-fill-lg': 'repeat(auto-fill, minmax(20rem, 1fr))'
			}
		}
	},
	plugins: [require("tailwindcss-animate")],
} satisfies Config;