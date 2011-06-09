//
//  FilterViewController.h
//  Stamped
//
//  Created by Kevin Palms on 2/10/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>


@protocol FilterViewDelegate;

@interface FilterViewController : UIViewController {

	id <FilterViewDelegate> delegate;
}

@property (assign) id <FilterViewDelegate> delegate;

- (id)initInManagedObjectContext:(NSManagedObjectContext *)context;
//- (IBAction)selectFilter:(NSString *)stampType;

@end


@protocol FilterViewDelegate <NSObject>

- (void)applyFilterOnStampType:(NSString *)stampType;

@end