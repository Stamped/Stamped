//
//  STOAuth.h
//  STOAuth
//
//  Created by Devin Doty on 11/25/11.
//  Copyright (c) 2011 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "EGOHTTPRequest.h"

@interface STOAuth : NSObject

+ (NSString*)MD5Hash:(NSString*)string;
+ (NSString *)encodedOAuthParameterForString:(NSString *)str;
+ (NSString *)stringWithBase64ForData:(NSData *)data;
+ (void)addParamValue:(id)value forName:(id)name toArray:(NSMutableArray*)array;
+ (NSString *)paramStringForParams:(NSArray *)params joiner:(NSString *)joiner shouldQuote:(BOOL)shouldQuote shouldSort:(BOOL)shouldSort;
+ (NSString *)signClearText:(NSString *)text withSecret:(NSString *)secret;
+ (NSString *)timestamp;
+ (NSString *)nonce;
+ (NSString *)normalizedRequestURLStringForRequest:(EGOHTTPRequest *)request;
+ (NSString *)signatureForParams:(NSMutableArray *)params request:(EGOHTTPRequest *)request token:(NSString*)token;
@end

@interface STOAuthParameter : NSObject {
@private
    NSString *name_;
    NSString *value_;
}

@property (nonatomic, copy) NSString *name;
@property (nonatomic, copy) NSString *value;

+ (STOAuthParameter *)parameterWithName:(NSString *)name value:(NSString *)value;
+ (NSArray *)sortDescriptors;
@end