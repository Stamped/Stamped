//
//  STAccountParameters.h
//  Stamped
//
//  Created by Landon Judkins on 6/6/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface STAccountParameters : NSObject

@property (nonatomic, readwrite, copy) NSString* screenName;
@property (nonatomic, readwrite, copy) NSString* name;
@property (nonatomic, readwrite, copy) NSString* email;
@property (nonatomic, readwrite, copy) NSString* phone;
@property (nonatomic, readwrite, copy) NSString* tempImageURL;
@property (nonatomic, readwrite, copy) NSString* bio;
@property (nonatomic, readwrite, copy) NSString* website;
@property (nonatomic, readwrite, copy) NSString* location;
@property (nonatomic, readwrite, copy) NSString* colorPrimary;
@property (nonatomic, readwrite, copy) NSString* colorSecondary;

- (NSMutableDictionary*)asDictionaryParams;

@end
