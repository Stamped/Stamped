//
//  FacebookUser.h
//  Stamped
//
//  Created by Andrew Bonventre on 1/16/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface FacebookUser : NSObject

@property (nonatomic, copy) NSString* name;
@property (nonatomic, copy) NSString* facebookID;
@property (nonatomic, copy) NSString* profileImageURL;

@end
