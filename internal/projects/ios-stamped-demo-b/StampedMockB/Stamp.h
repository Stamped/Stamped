//
//  Stamp.h
//  StampedMockB
//
//  Created by Kevin Palms on 6/28/11.
//  Copyright (c) 2011 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>


@interface Stamp : NSManagedObject {
@private
}
@property (nonatomic, retain) NSString * title;
@property (nonatomic, retain) NSString * subTitle;
@property (nonatomic, retain) NSString * avatar;
@property (nonatomic, retain) NSNumber * userID;
@property (nonatomic, retain) NSString * comment;
@property (nonatomic, retain) NSString * stampImage;
@property (nonatomic, retain) NSString * category;
@property (nonatomic, retain) NSNumber * hasPhoto;
@property (nonatomic, retain) NSNumber * hasMention;
@property (nonatomic, retain) NSNumber * hasRestamp;
@property (nonatomic, retain) UIColor * color;
@property (nonatomic, retain) NSString * userName;

+ (void)addStampWithData:(NSDictionary *)stampData inManagedObjectContext:(NSManagedObjectContext *)context;

@end
