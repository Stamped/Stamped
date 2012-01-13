//
//  TwitterUser.h
//  Stamped
//
//  Created by Andrew Bonventre on 1/12/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface TwitterUser : NSObject

@property (nonatomic, copy) NSString* name;
@property (nonatomic, copy) NSString* screenName;
@property (nonatomic, copy) NSString* profileImageURL;

@end
