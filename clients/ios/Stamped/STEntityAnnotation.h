//
//  STEntityAnnotation.h
//  Stamped
//
//  Created by Landon Judkins on 6/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <MapKit/MapKit.h>
#import "STEntityDetail.h"

@interface STEntityAnnotation : NSObject <MKAnnotation, NSCoding>

- (id)initWithEntityDetail:(id<STEntityDetail>)entityDetail;

@property (nonatomic, readonly, retain) id<STEntityDetail> entityDetail;

@end
