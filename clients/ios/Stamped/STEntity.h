//
//  STEntity.h
//  Stamped
//
//  Created by Landon Judkins on 4/2/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STImageList.h"

@protocol STEntity <NSObject>

@required

@property (nonatomic, readonly, retain) NSString* entityID;
@property (nonatomic, readonly, retain) NSString* title;
@property (nonatomic, readonly, retain) NSString* subtitle;
@property (nonatomic, readonly, retain) NSString* category;
@property (nonatomic, readonly, retain) NSString* subcategory;
@property (nonatomic, readonly, retain) NSString* coordinates;

@property (nonatomic, readonly, copy) NSArray<STImageList>* images;

@end
