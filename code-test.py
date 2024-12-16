def calculate_area(radius):
    pi = 3.14
    area = pi * radius * radius
    return area

def main():
    while True:
        try:
            radius = float(input("Enter the radius: "))
            if radius < 0:
                print("Radius cannot be negative!")
                continue
            area = calculate_area(radius)
            print(f"The area is: {area}")

            if area > 0:
                print("The area is positive.")
            elif area == 0:
                print("The area is zero.")
            else:
                print("The area can't be negative.")

        except ValueError:
            print("Invalid input! Please enter a numeric value.")

        repeat = input("Do you want to enter another radius? (yes/no): ").strip().lower()
        if repeat != 'yes':
            break

    print("Done!")

main()
