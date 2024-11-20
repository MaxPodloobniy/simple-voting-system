import pandas as pd
import numpy as np
from crypto_tools import *


class VotingCommision:
    def __init__(self, voters_list, signatures_list, candidates_list):
        self.voters_data = pd.DataFrame({'Name': voters_list,
                                         'Public_Signature': signatures_list,
                                         'Is_Voted': np.zeros(len(voters_list))})
        self.candidates_data = pd.DataFrame({'Name': candidates_list,
                                             'Votes_Count': np.zeros(len(candidates_list))})


    def count_vote(self, encrypted_ballot, signature):
        """Дешифрує бюлетень, перевіряє виборця, додає голос кандидату"""
        decrypted_text = decrypt_message_gamma(encrypted_ballot, 'SECRET')

        # Перевіряємо чи існує кандидат і чи він ще не голосував
        voter_id = self.check_voter(decrypted_text, signature)

        lines = decrypted_text.split('\n')

        # Проходимось по всім строкам бюлетеня
        for line in lines:
            # Знаходимо строку де введений номер кандидата
            if "Ваш вибір:" in line:
                candidate_number = line.split('Ваш вибір: ')[-1].strip()
                number = int(candidate_number)

                if 1 <= number <= len(self.candidates_data):
                    # Збільшуємо лічильник голосів для кандидата
                    self.candidates_data.loc[number - 1, 'Votes_Count'] += 1
                    # Ставимо виборцю флажок що вже проголосував
                    self.voters_data.loc[voter_id, 'Is_Voted'] = 1
                else:
                    raise ValueError(f"Кандидата під нормером {number} не існує")

    def check_voter(self, ballot_text, voter_signature):
        """Проходить по всім публічним ключам виборців, перевіряє чи хоч один підходить, знаходить
        виборця і перевіряє чи не голосував вже він"""
        # Створюємо список перевірки всіх наявних публічних ключів(бо не знаємо якого виборця підпис)
        is_valid_signature_list = [verify_signature(sig, ballot_text, voter_signature) for sig in
                                   self.voters_data['Public_Signature']]

        # Якщо виборець існує в списках
        if any(is_valid_signature_list):
            voter_index = is_valid_signature_list.index(True)

            # Якщо виборець ще не голосував
            if self.voters_data.loc[voter_index, 'Is_Voted'] == 0:
                return voter_index
            else:
                raise ValueError("Виборець під таким номером вже голосував")
        else:
            raise ValueError("Виборця під таким номером не існує в виборчих списках")

    def get_results(self):
        """Передає результати голосування"""
        num_of_lost_votes = (self.voters_data['Is_Voted'] == 1).sum()

        return self.candidates_data, num_of_lost_votes
