//
//  STEntitySearchSection.h
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STEntitySearchResult.h"

@protocol STEntitySearchSection <NSObject>

@property (nonatomic, readonly, copy) NSString* title;
@property (nonatomic, readonly, copy) NSString* subtitle;
@property (nonatomic, readonly, copy) NSString* imageURL;
@property (nonatomic, readonly, copy) NSArray<STEntitySearchResult>* entities;

@end
