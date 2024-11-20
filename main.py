import pandas as pd
import matplotlib.pyplot as plt
from commission import VotingCommision
from voter import Voter
from crypto_tools import *


def generate_ballot_text(voter_choice, candidates_data):
    """Генерує текст бюлетеня з переліком кандидатів."""
    # Створюємо заголовок бюлетеня
    ballot_text = "БЮЛЕТЕНЬ ДЛЯ ГОЛОСУВАННЯ\n\n"

    # Додаємо перелік кандидатів з їх номерами
    for candidate in candidates_data:
        ballot_text += f"{candidate}\n"

    # Додаємо інструкцію для голосування
    ballot_text += "\nВведіть номер кандидата, за якого ви голосуєте:\n"
    ballot_text += f"Ваш вибір: {voter_choice}"

    return ballot_text


def main():
    voters_names = pd.read_excel('data/voters.xlsx')
    candidates_names = pd.read_excel('data/candidates.xlsx')
    voters_obj_list = []
    public_signatures = []

    # Перетворюємо Series в список
    voters_list = voters_names['Voters'].tolist()
    candidates_list = candidates_names['Candidates'].tolist()

    for voter_name in voters_list:
        voter_obj = Voter(voter_name)
        voter_sign = voter_obj.public_sign
        voters_obj_list.append(voter_obj)
        public_signatures.append(voter_sign)

    commision = VotingCommision(voters_list, public_signatures, candidates_list)

    print('Систему запущено')
    print(f'Знайдено кандидатів: {len(candidates_list)}')
    print(f'Знайдено Виборців: {len(voters_list)}')

    while True:
        # ----------------------- Авторизація виборця -----------------------

        print('\nЗареєструйтесь, для цього введіть свій номер виборця')
        print(f'Всього зареєстровано {len(voters_list)} виборців')
        voters_num = input('Введіть свій номер виборця ')

        # Перевіряємо чи це число
        if not str(voters_num).isdigit():
            raise ValueError("Номер виборця має бути цілим числом")
        voters_num = int(voters_num)

        # Перевіряємо чи номер в межах допустимого діапазону
        if voters_num < 1 or voters_num > voters_names.shape[0]+1:
            raise ValueError(f"Номер виборця має бути від 1 до {voters_names.shape[0]}")

        print('\nАвторизація успішна!\n')

        # ----------------------- Процес голосування -----------------------

        print('Список кандидатів:')
        for name in candidates_names['Candidates']:
            print(name)
        voters_choice = input('Введіть номер обраного кандидата ')

        # Перевіряємо чи це число
        if not str(voters_choice).isdigit():
            raise ValueError("Номер кандидата має бути цілим числом")
        voters_choice = int(voters_choice)

        # Перевіряємо чи номер в межах допустимого діапазону
        if voters_choice < 1 or voters_choice > candidates_names.shape[0]+1:
            raise ValueError(f"Номер кандидата має бути від 1 до {candidates_names.shape[0]}")

        # ----------------------- Обробка голосу і підрахунок голосів -----------------------

        voters_ballot = generate_ballot_text(voters_choice, candidates_list)
        encrypted_ballot = encrypt_message_gamma(voters_ballot, 'SECRET')

        voters_signature = voters_obj_list[voters_num-1].sign_message(voters_ballot)

        commision.count_vote(encrypted_ballot, voters_signature)
        print("Ваш голос враховано!")

        # ----------------------- Продовження роботи -----------------------

        code = input("Якщо хочете завершити голосування введіть- 1, продовжити - 2")

        # Перевіряємо чи це число
        if not str(code).isdigit():
            raise ValueError("Код має бути цілим числом")
        code = int(code)

        if code == 1:
            candidates_votes, num_of_lost = commision.get_results()

            # Візуалізуємо результати голосувань
            plt.figure(figsize=(10, 6))
            plt.bar(candidates_votes['Name'], candidates_votes['Votes_Count'])
            plt.title('Голоси кандидатів')
            plt.xlabel('Кандидати')
            plt.ylabel('Кількість голосів')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.show()

            index_of_winner = candidates_votes['Votes_Count'].idxmax()
            print(f"Найбільше голосів у {candidates_votes.loc[index_of_winner, 'Name']}")
            print(f"Явка склала {num_of_lost} чол. або {num_of_lost/len(voters_list)}%")

            exit()
        elif code == 2:
            continue
        else:
            raise ValueError(f"Не правильно введений код")


if __name__ == '__main__':
    main()