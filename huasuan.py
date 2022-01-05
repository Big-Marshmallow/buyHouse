'''
A toy program to understand if rental or buying a house costs less,
assuming only living for a certain duration

TODO:
1. factor in investment return of downpayment
2. factor in tax reduction
3. factor in cost of agent
4. factor in cost of remodeling

Assumes:
1. Rental price goes up by monthly inflation rate
'''

LIVING_MONTH = 60

INFLATION_RATE = 0.025
INITIAL_MONTHLY_RENT = 3300

TOTAL_HOUSE_PRICE = 900000
ANNUAL_INTEREST_RATE = 0.035
MORGAGE_TERMS = 360 # 30 years
DOWNPAYMENT_PCT = 0.2
MONTHLY_HOA = 500
MONTHLY_INSURANCE = 60
ANNUAL_PROPERTY_TAX_RATE = 0.0073

# dynamic table for different kinds of cost
costOfMonth = list()
principleOfMonth = list()
interestOfMonth = list()
propertyTaxOfMonth = list()


def getMonthlyPaymentToBank(total, downpaymentPct, loanTermInMonth, AnnualInterestRate):
    '''
    Calculate monthly payment to bank (including both principle and interest)
    reference: https://www.bankrate.com/calculators/mortgages/mortgage-calculator.aspx

    Note that monthly payment is a constant across the morgage schedule, but the
    percentage of principle and interest changes across the loan term. The
    percentage of the interest goes down as principle is paid.

    @total: total price of the bought house
    @downpaymentPct: percentage of downpayment
    @loanTermInMonth: number of months for morgage schedule (30 years -> 360 months)
    @AnnualInterestRate: as its name suggests

    @return: monthly payment to bank (including principle and interest)
    '''

    morgage = total * (1 - downpaymentPct)
    r = AnnualInterestRate / 12 # monthly interest rate
    return morgage * (r * (1 + r) ** loanTermInMonth) / ((1 + r) ** loanTermInMonth - 1)


def initCostOfRental(termInMonth, inflationRate, initialRent):
    '''
    Build the monthly rental cost table

    @termInMonth: number of months to live in the rental property
    @inflationRate: as its name suggests
    @initialRent: price of the rent for the first month

    @return: total cost of renting
    '''

    rent = initialRent
    for month in range(0, termInMonth):
        costOfMonth.append(int(rent))
        rent = rent * ((1 + inflationRate / 12))


def initCostOfBank(termInMonth, total, downpaymentPct, loanTermInMonth, AnnualInterestRate):
    '''
    Build the monthly payment to bank in interest and principle

    @termInMonth: number of months to live in the rental property
    @total: total price of house
    @downpaymentPct: percentage of downpayment
    @loanTermInMonth: number of months to pay off debt
    @AnnualInterestRate: as its name suggests
    '''
    morgage = total * (1 - downpaymentPct)

    monthlyPayment = getMonthlyPaymentToBank(total,
                                             downpaymentPct,
                                             loanTermInMonth,
                                             AnnualInterestRate)

    for month in range(0, termInMonth):
        interestOfTheMonth = morgage * AnnualInterestRate / 12
        principleOfTheMonth = monthlyPayment - interestOfTheMonth

        morgage -= principleOfTheMonth

        interestOfMonth.append(int(interestOfTheMonth))
        principleOfMonth.append(int(principleOfTheMonth))


def initPropertyTax(termInMonth, total, propertyTaxRate, inflationRate):
    '''
    Build lookup table for the monthly payment for property tax

    Reference: https://smartasset.com/taxes/california-property-tax-calculator

    @termInMonth: number of months to live in the rental property
    @total: total price of house
    @propertyTaxRate: as its name suggests
    @inflationRate: as its name suggests
    '''

    # California law (Proposition 13) limits the assessed value of
    # property cannot increase by more than 2% every year.
    assessedValueIncRate = 0.02
    incRate = min(assessedValueIncRate, inflationRate)

    for month in range(0, termInMonth):
        tax = total * propertyTaxRate / 12
        propertyTaxOfMonth.append(int(tax))

        total *= (1 + incRate / 12)


def init():
    '''
    Initialize various lookup table
    '''

    initCostOfRental(LIVING_MONTH,
                     INFLATION_RATE,
                     INITIAL_MONTHLY_RENT)

    initCostOfBank(LIVING_MONTH,
                   TOTAL_HOUSE_PRICE,
                   DOWNPAYMENT_PCT,
                   MORGAGE_TERMS,
                   ANNUAL_INTEREST_RATE)

    initPropertyTax(LIVING_MONTH,
                    TOTAL_HOUSE_PRICE,
                    ANNUAL_PROPERTY_TAX_RATE,
                    INFLATION_RATE)


def getRentalCostByMonth(month):
    return costOfMonth[month]


def getInterestCostByMonth(month):
    return interestOfMonth[month]


def getPrincipleCostByMonth(month):
    return principleOfMonth[month]


def getPropertyTaxByMonth(month):
    return propertyTaxOfMonth[month]


def getHOAByMonth(month):
    # Assumes HOA increases in the same pace as inflation
    return MONTHLY_HOA * (1 + INFLATION_RATE / 12) ** month


def getInsuranceByMonth(month):
    # Assumes insurance increases in the same pace as inflation
    return MONTHLY_INSURANCE * (1 + INFLATION_RATE / 12) ** month


def getTotalRentalCost(termInMonth):
    '''
    Print the monthly breakdown for living by rental.

    @return: total cost of living by rental
    '''

    cost = 0
    print("############################")
    print("MONTHLY PAYMENT FOR RENTAL")
    print("############################")
    print("Month | Cost   ")
    print("############################")
    for month in range(0, termInMonth):
        rental = getRentalCostByMonth(month)

        cost += rental

        print("%5d | %6d " % \
              (month, rental))

    return cost

def getTotalHousingCost(termInMonth):
    '''
    Print the monthly cost of buying and holding a house.

    @return: total cost of buying and holding a house for "termInMonth" months.
    @return: total pure cost of (excluding principle) of owning a house.
    '''

    pureCost = 0 # does not include principle, count it as savings
    totalCost = 0 # every dollar spent

    print("#####################################################################")
    print("MONTHLY PAYMENT BREAKDOWN FOR BUYING A HOUSE")
    print("#####################################################################")
    print("Month | Interest | Principle | Property Tax | HOA | Insurance | Total")
    print("#####################################################################")

    for month in range(0, termInMonth):
        interest = getInterestCostByMonth(month)
        principle = getPrincipleCostByMonth(month)
        tax = getPropertyTaxByMonth(month)
        hoa = getHOAByMonth(month)
        insurance = getInsuranceByMonth(month)
        total = interest + principle + tax + hoa + insurance

        print("%5d | %8d | %9d | %12d | %3d | %9d | %5d" % \
              (month, interest, principle, tax, hoa, insurance, total))

        pureCost += total - principle
        totalCost += total

    return totalCost, pureCost


def main():
    init()

    totalRentalCost = getTotalRentalCost(LIVING_MONTH)
    totalHousingCost, pureHousingCost = getTotalHousingCost(LIVING_MONTH)

    print("To live %d months" % LIVING_MONTH)
    print("Total cost of rental %d" % totalRentalCost)
    print("Total cost of buying a house %d" % (totalHousingCost + TOTAL_HOUSE_PRICE * DOWNPAYMENT_PCT))
    print("Pure cost of buying a house %d (exclude principle and downpayment)" % pureHousingCost)


if __name__ == "__main__":
    main()

