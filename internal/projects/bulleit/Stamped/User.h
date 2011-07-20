//
//  User.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/19/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>


@interface ImageToDataTransformer : NSValueTransformer
@end

@interface User : NSManagedObject

@property (nonatomic, retain) NSString* bio;
@property (nonatomic, retain) NSString* displayName;
@property (nonatomic, retain) NSString* primaryColor;
@property (nonatomic, retain) NSString* firstName;
@property (nonatomic, retain) NSString* lastName;
@property (nonatomic, retain) NSString* userID;
@property (nonatomic, retain) NSString* website;
@property (nonatomic, retain) NSString* secondaryColor;
@property (nonatomic, retain) NSString* profileImageURL;
@property (nonatomic, retain) UIImage* profileImage;
@property (nonatomic, retain) NSString* screenName;
@property (nonatomic, retain) UIImage* stampImage;
@property (nonatomic, retain) NSSet* Stamps;
@end

@interface User (CoreDataGeneratedAccessors)

- (void)addStampsObject:(NSManagedObject*)value;
- (void)removeStampsObject:(NSManagedObject*)value;
- (void)addStamps:(NSSet*)values;
- (void)removeStamps:(NSSet*)values;
@end
