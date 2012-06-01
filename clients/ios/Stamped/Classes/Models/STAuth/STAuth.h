//
//  STAuth.h
//  Stamped
//
//  Created by Devin Doty on 5/31/12.
//
//

#import <Foundation/Foundation.h>

@interface STAuth : NSObject

+ (id)sharedInstance;

- (void)facebookSignupWithParams:(NSDictionary*)params;
- (void)twitterSignupWithParams:(NSDictionary*)params;
- (void)twitterAuthWithToken:(NSString*)token secretToken:(NSString*)secretToken;
- (void)facebookAuthWithToken:(NSString*)token;

@end
