/*
 * Refactor base on MACROS
 gcc ecdsa.c -o ecdsa.out -L/usr/local/lib -lssl -lcrypto
 */

#include <openssl/conf.h>
#include <openssl/evp.h>
#include <openssl/err.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <stdint.h>

// To switch from encryption to decryption benchmarks, undefine the following.
#define ENCRYPT_MODE

// Define the encryption method for benchmarks
#define CRYPTO_METHOD EVP_aes_256_ctr

// Key size for benchmark: 16, 24 or 32
#define KEY_SIZE (32)

//
uint64_t rdtsc(){
    unsigned int lo,hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((uint64_t)hi << 32) | lo;
}

void handleErrors(void)
{
  ERR_print_errors_fp(stderr);
  abort();
}


void fill_with_random(unsigned char *stream, int n)
{
  size_t i;
  for (i = 0; i < n; i++)
  {
    stream[i] = (unsigned char) (rand() % 255 + 1);
  }
  stream[n] = 0;
}


// note that we can't have a 0 value byte only at stream end
unsigned char* gen_random_bytestream(int num_bytes)
{
  /* make sure we don't include a 0 */
  unsigned char* stream=malloc(num_bytes + 1);
  if (stream == NULL)
    {
        printf("ERROR : Could not allocate memory for random buffer !");
    }

    /*
  size_t i;
  for (i = 0; i < num_bytes; i++)
  {
    stream[i] = (unsigned char) (rand() % 255 + 1);
  }

  stream[num_bytes] = 0;
*/
    fill_with_random(stream, num_bytes);
  return stream;
}


// can we pass the encryption function as param?
int decrypt(unsigned char *ciphertext, int ciphertext_len, unsigned char *key,
  unsigned char *iv, unsigned char *plaintext)
{
  EVP_CIPHER_CTX *ctx;

  int len;

  int plaintext_len;

  /* Create and initialise the context */
  if(!(ctx = EVP_CIPHER_CTX_new())) handleErrors();

  /* Initialise the decryption operation. IMPORTANT - ensure you use a key
   * and IV size appropriate for your cipher
   * In this example we are using 256 bit AES (i.e. a 256 bit key). The
   * IV size for *most* modes is the same as the block size. For AES this
   * is 128 bits */
  if(1 != EVP_DecryptInit_ex(ctx, CRYPTO_METHOD(), NULL, key, iv))
    handleErrors();

  /* Provide the message to be decrypted, and obtain the plaintext output.
   * EVP_DecryptUpdate can be called multiple times if necessary
   */
  if(1 != EVP_DecryptUpdate(ctx, plaintext, &len, ciphertext, ciphertext_len))
    handleErrors();
  plaintext_len = len;

  /* Finalise the decryption. Further plaintext bytes may be written at
   * this stage.
   */
  if(1 != EVP_DecryptFinal_ex(ctx, plaintext + len, &len)) handleErrors();
  plaintext_len += len;

  /* Clean up */
  EVP_CIPHER_CTX_free(ctx);

  return plaintext_len;
}


int encrypt(unsigned char *plaintext, int plaintext_len, unsigned char *key,
  unsigned char *iv, unsigned char *ciphertext)
{
  EVP_CIPHER_CTX *ctx;

  int len;
  int ciphertext_len;

  if(!(ctx = EVP_CIPHER_CTX_new())) handleErrors();
  if(1 != EVP_EncryptInit_ex(ctx, CRYPTO_METHOD(), NULL, key, iv))
    handleErrors();
  if(1 != EVP_EncryptUpdate(ctx, ciphertext, &len, plaintext, plaintext_len))
    handleErrors();
  ciphertext_len = len;
  if(1 != EVP_EncryptFinal_ex(ctx, ciphertext + len, &len)) handleErrors();
  ciphertext_len += len;

  EVP_CIPHER_CTX_free(ctx);
  return ciphertext_len;
}


int main (void)
{
    // library initialization, not included in timing
    ERR_load_crypto_strings();
    OpenSSL_add_all_algorithms();
    // config is deprecated as of v1.1
    //OPENSSL_config(NULL);

    // test parameters
    //int         data_size = 1024 * 1024;
    int         repetitions = 50;

    int         key_size = 16; // not enough, there are different calls per key size
    int         iv_size = 16; // should be identical to AES block size, i.e. 128 bits

    clock_t     start_time, end_time;
    double      cpu_time_used;
    double      total_time = 0;

    uint64_t    start_cycles, end_cycles, total_cycles;
    uint64_t    start_cycles_decrypt, end_cycles_decrypt, total_cycles_decrypt;
    uint64_t    cycles_avg = 0;
    int data_size_kb;
   // for(data_size_kb=64 * 1024; data_size_kb>=1024; data_size_kb-=1024)

   int tmp_hack = 0;

    for(data_size_kb=512; data_size_kb<=64 * 1024; data_size_kb+=512)
    {
        int data_size = 1024 * data_size_kb;

        unsigned char *rand_plaintxt = gen_random_bytestream(data_size);
        unsigned char *ciphertext = (unsigned char *)malloc(data_size + 1);
            ciphertext[data_size] = 0;
        unsigned char *decryptedtext = (unsigned char *)malloc(data_size + 1);
        int plaintext_len = strlen ((char *)rand_plaintxt);

        total_time = 0;
        total_cycles = 0;
        total_cycles_decrypt = 0;

        for(int r=0; r<repetitions; r++)
        {
            unsigned char *_k = gen_random_bytestream(KEY_SIZE);
            unsigned char *_iv = gen_random_bytestream(16);

            // within experiments it doesnt make any difference randomizing
            // each time, therefore commenting the randomization for speed
            // fill_with_random(rand_plaintxt, data_size);

            // do an encrypt for mearusing TIME ticks
            //start_time = clock();
            //encrypt(rand_plaintxt, plaintext_len, _k, _iv, ciphertext);
            //end_time = clock();
            //double time_taken = (double)(end_time - start_time)/CLOCKS_PER_SEC;
            //total_time += time_taken;

            // do an ecrypt for measuring CYCLES
            start_cycles = rdtsc();
            int len = encrypt(rand_plaintxt, plaintext_len, _k, _iv, ciphertext);
            end_cycles = rdtsc();
            total_cycles += (end_cycles - start_cycles);

            // quick hack: make sure the compiler doesnt optimize the ciphertext
            int tmp_len = strlen ((char *)rand_plaintxt);
            tmp_hack += tmp_len;

            // measure decrypt CYCLES
            start_cycles_decrypt = rdtsc();
            decrypt(ciphertext, len, _k, _iv, decryptedtext);
            end_cycles_decrypt = rdtsc();
            total_cycles_decrypt += (end_cycles_decrypt - start_cycles_decrypt);

            // quick hack: verify decryption
            int tmp_dec_len = strlen ((char *)decryptedtext);
            if (memcmp(decryptedtext, rand_plaintxt, plaintext_len) != 0)
            {
                printf("DECRYPTION FAILED %d %d\n", plaintext_len, tmp_dec_len);
                handleErrors();
            }
        }

        free(rand_plaintxt);
        free(ciphertext);
        free(decryptedtext);

        double avg_time = total_time/repetitions;
        double avg_cycles = (double)total_cycles/repetitions;
        double avg_cpb = ((double)total_cycles/repetitions)/data_size;
        double mb_s = (((double)(data_size * repetitions))/total_time) / (1024 * 1024);
        double avg_cycles_decrypt = (double)total_cycles_decrypt/repetitions;
        //printf("%12d size: %8f %8f %8f %8f\n", data_size, avg_time, avg_cycles, avg_cpb, mb_s);

        printf("%8f\n", avg_cycles);
        //printf("%8f\n", avg_cycles_decrypt);
    }

  printf("Finished %d\n", tmp_hack);

  // library shutdown - should not be timed
  EVP_cleanup();
  ERR_free_strings();

  return 0;
}
