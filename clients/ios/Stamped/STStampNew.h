//
//  STStampNew.h
//  Stamped
//
//  Created by Landon Judkins on 4/19/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STImageUpload.h"

@interface STStampNew : STImageUpload

@property (nonatomic, readwrite, copy) NSString* entityID;
@property (nonatomic, readwrite, copy) NSString* searchID;
@property (nonatomic, readwrite, copy) NSString* blurb;
@property (nonatomic, readwrite, copy) NSString* credit;

- (void)addCreditWithScreenName:(NSString*)screenName;

@end
