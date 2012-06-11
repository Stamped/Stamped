//
//  STAuth.h
//  Stamped
//
//  Created by Devin Doty on 5/31/12.
//
//

#import <Foundation/Foundation.h>
#import "STAccountParameters.h"

typedef void(^STAuthRequestFinished)(NSError *);

@interface STAuth : NSObject

+ (id)sharedInstance;


/*
 * Sign up
 */
- (void)signupWithPassword:(NSString*)password parameters:(STAccountParameters*)params;
- (void)facebookSignupWithToken:(NSString*)token params:(STAccountParameters*)params;
- (void)twitterSignupWithToken:(NSString*)token secretToken:(NSString*)secretToken params:(STAccountParameters*)params;

/*
 * Login
 */
- (void)twitterAuthWithToken:(NSString*)token secretToken:(NSString*)secretToken completion:(STAuthRequestFinished)completion;
- (void)facebookAuthWithToken:(NSString*)token completion:(STAuthRequestFinished)completion;

/*
 * Updates
 */
- (void)checkUserName:(NSString*)username completion:(STAuthRequestFinished)completion;
- (void)updateStampWithPrimaryColor:(NSString*)primary secondary:(NSString*)secondary completion:(STAuthRequestFinished)completion;
- (void)updateProfileImageWithPath:(NSString*)tempPath completion:(STAuthRequestFinished)completion;



@end
